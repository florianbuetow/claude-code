import subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).parent
SCRIPT = ROOT / "check_corpus_contract.py"

def run(case):
    d = ROOT / "fixtures" / "contract" / case
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--corpus", str(d), "--references", str(d), "--coverage", str(d / "COVERAGE.md")],
        capture_output=True, text=True)

def test_good_passes():
    assert run("good").returncode == 0

def test_missing_source_fails():
    r = run("bad-missing-source"); assert r.returncode == 1 and "Source:" in r.stdout

def test_verbatim_fails():
    r = run("bad-verbatim"); assert r.returncode == 1 and "verbatim" in r.stdout.lower()

def test_coverage_gap_fails():
    r = run("bad-coverage"); assert r.returncode == 1 and "coverage" in r.stdout.lower()

if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in [
        ("test_good_passes", test_good_passes),
        ("test_missing_source_fails", test_missing_source_fails),
        ("test_verbatim_fails", test_verbatim_fails),
        ("test_coverage_gap_fails", test_coverage_gap_fails),
    ]:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            failures += 1
            print(f"FAIL  {name}: {e}")
            traceback.print_exc()
    if failures:
        print(f"\n{failures} test(s) FAILED")
        raise SystemExit(1)
    print(f"\n4 passed")
