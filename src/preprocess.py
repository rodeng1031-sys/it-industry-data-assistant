"""Preprocess raw statistics for the Korean IT/SI time-series project.

Raw files in data/raw/ are read only. Processed outputs are written to data/processed/.
Outputs:
- service_production_long.csv
- job_demand_long.csv
- merged_monthly.csv
"""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

SERVICE_INDUSTRIES = {
    "정보통신업": "information_communication",
    "소프트웨어 개발 및 공급업": "software_development_supply",
    "컴퓨터 프로그래밍, 시스템 통합 및 관리업": "computer_programming_system_integration",
    "정보서비스업": "information_service",
}
INDEX_TYPES = {
    "경상지수": "current_index",
    "불변지수": "constant_index",
    "계절조정지수": "seasonally_adjusted_index",
}
MAIN_IT_OCCUPATIONS = {
    "2007직종_정보통신 관련직 전체",
    "2018직종_정보통신 연구개발직 및 공학기술직 전체",
    "2025직종_정보통신 연구개발직 및 공학기술직 전체",
}
SOFTWARE_OCCUPATIONS = {
    "2007직종_소프트웨어개발전문가",
    "2018직종_소프트웨어 개발자",
    "2025직종_소프트웨어 개발자",
}


def parse_month(label: str) -> pd.Timestamp:
    m = re.search(r"(\d{4})[.년\-\s]+(\d{1,2})", str(label))
    if not m:
        raise ValueError(f"월 라벨 해석 실패: {label}")
    return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)


def resolve_duplicates(df: pd.DataFrame, keys: list[str], value_col: str, name: str) -> pd.DataFrame:
    dup = df.duplicated(keys, keep=False)
    if not dup.any():
        return df.copy()
    conflicts = df[dup].groupby(keys, dropna=False)[value_col].nunique(dropna=False)
    conflicts = conflicts[conflicts > 1]
    if not conflicts.empty:
        raise ValueError(f"{name}: 동일 키에 다른 값이 있어 임의 병합하지 않음\n{conflicts.head(10)}")
    return df.drop_duplicates(keys + [value_col], keep="first").copy()


def find_service_csv() -> Path:
    candidates = []
    for p in RAW_DIR.glob("*.csv"):
        try:
            cols = list(pd.read_csv(p, encoding="cp949", nrows=0).columns)
        except UnicodeDecodeError:
            continue
        month_cols = [c for c in cols if re.match(r"^\d{4}\.\d{2} 월$", str(c))]
        if {"업종별", "항목"}.issubset(cols) and len(month_cols) >= 100:
            candidates.append(p)
    if not candidates:
        raise FileNotFoundError("100개월 이상 월별 컬럼이 있는 KOSIS 서비스업생산지수 CSV가 필요합니다.")
    return max(candidates, key=lambda p: p.stat().st_size)


def preprocess_service() -> pd.DataFrame:
    path = find_service_csv()
    df = pd.read_csv(path, encoding="cp949")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    months = [c for c in df.columns if re.match(r"^\d{4}\.\d{2} 월$", str(c))]
    df = df[df["업종별"].isin(SERVICE_INDUSTRIES) & df["항목"].isin(INDEX_TYPES)].copy()

    long = df.melt(["업종별", "항목"], months, "month_label", "value")
    long["date"] = long["month_label"].map(parse_month)
    long["industry_ko"] = long["업종별"]
    long["industry"] = long["업종별"].map(SERVICE_INDUSTRIES)
    long["index_type_ko"] = long["항목"]
    long["index_type"] = long["항목"].map(INDEX_TYPES)
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long["source"] = "KOSIS 서비스업동향조사 서비스업생산지수"
    long["source_file"] = path.name

    out = long[["date", "industry", "industry_ko", "index_type", "index_type_ko", "value", "source", "source_file"]]
    out = resolve_duplicates(out, ["date", "industry", "index_type"], "value", "service")
    return out.sort_values(["industry", "index_type", "date"])


def col_index(cell_ref: str) -> int:
    n = 0
    for ch in "".join(re.findall(r"[A-Z]+", cell_ref)):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_ooxml_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(NS + "si"):
                shared.append("".join(t.text or "" for t in si.findall(".//" + NS + "t")))
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in root.findall(".//" + NS + "row"):
            vals = []
            for cell in row.findall(NS + "c"):
                idx = col_index(cell.attrib["r"])
                while len(vals) <= idx:
                    vals.append("")
                v = cell.find(NS + "v")
                value = "" if v is None else v.text or ""
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                vals[idx] = value
            rows.append(vals)
    return rows


def read_job_file(path: Path) -> pd.DataFrame:
    rows = read_ooxml_rows(path)
    header = ["마감년월", "직종_중분류", "직종_소분류", "구인인원(월)", "구직건수(월)", "취업건수(월)"]
    start = next((i for i, r in enumerate(rows) if r[:6] == header), None)
    if start is None:
        raise ValueError(f"구인구직 표 헤더를 찾지 못함: {path}")

    records = []
    month, middle = "", ""
    for r in rows[start + 1 :]:
        r = r + [""] * 6
        if r[0]:
            month = r[0]
        if r[1]:
            middle = r[1]
        if not any(r[:6]) or month == "총계" or "전체" in month:
            continue
        records.append({
            "month_label": month,
            "occupation_middle": middle,
            "occupation_small": r[2],
            "job_openings": r[3],
            "job_seekers": r[4],
            "placements": r[5],
            "source_file": path.name,
        })
    return pd.DataFrame(records)


def classify_job(row: pd.Series) -> str | None:
    if row["occupation_middle"] in MAIN_IT_OCCUPATIONS:
        return "it_broad"
    if row["occupation_small"] in SOFTWARE_OCCUPATIONS:
        return "software_developer"
    return None


def preprocess_jobs() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("직종별_구인구직취업현황*"))
    if not files:
        raise FileNotFoundError("직종별_구인구직취업현황 원본 파일이 필요합니다.")
    raw = pd.concat([read_job_file(p) for p in files], ignore_index=True)
    raw["indicator"] = raw.apply(classify_job, axis=1)
    raw = raw[raw["indicator"].notna()].copy()
    raw["date"] = raw["month_label"].map(parse_month)
    for c in ["job_openings", "job_seekers", "placements"]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")

    out = raw[["date", "indicator", "occupation_middle", "occupation_small", "job_openings", "job_seekers", "placements", "source_file"]]
    out = resolve_duplicates(out, ["date", "indicator"], "job_openings", "jobs")
    out = out.drop_duplicates(["date", "indicator"], keep="first").copy()
    out["opening_to_seeker_ratio"] = out["job_openings"] / out["job_seekers"]
    out["source"] = "한국고용정보원 고용행정통계 직종별 구인구직취업현황(월)"
    return out.sort_values(["indicator", "date"])


def make_merged(service: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    svc = service[service["index_type"] == "constant_index"].pivot_table(
        index="date", columns="industry", values="value", aggfunc="first"
    ).reset_index()
    svc = svc.rename(columns={c: f"service_{c}" for c in svc.columns if c != "date"})

    job_open = jobs.pivot_table(index="date", columns="indicator", values="job_openings", aggfunc="first").reset_index()
    job_open = job_open.rename(columns={"it_broad": "job_openings_it_broad", "software_developer": "job_openings_software_developer"})

    ratio = jobs.pivot_table(index="date", columns="indicator", values="opening_to_seeker_ratio", aggfunc="first").reset_index()
    ratio = ratio.rename(columns={"it_broad": "opening_to_seeker_ratio_it_broad", "software_developer": "opening_to_seeker_ratio_software_developer"})

    return svc.merge(job_open, on="date", how="left").merge(ratio, on="date", how="left").sort_values("date")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    service = preprocess_service()
    jobs = preprocess_jobs()
    merged = make_merged(service, jobs)

    service.to_csv(OUT_DIR / "service_production_long.csv", index=False, encoding="utf-8-sig")
    jobs.to_csv(OUT_DIR / "job_demand_long.csv", index=False, encoding="utf-8-sig")
    merged.to_csv(OUT_DIR / "merged_monthly.csv", index=False, encoding="utf-8-sig")

    print("[OK] service_production_long.csv", service.shape, service["date"].min().date(), service["date"].max().date())
    print("[OK] job_demand_long.csv", jobs.shape, jobs["date"].min().date(), jobs["date"].max().date())
    print("[OK] merged_monthly.csv", merged.shape, merged["date"].min().date(), merged["date"].max().date())
    print("[NOTE] processed CSV files are ignored by git until data license policy is confirmed.")


if __name__ == "__main__":
    main()
