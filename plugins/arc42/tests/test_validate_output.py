import subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).parent
SCRIPT = ROOT / "validate_output.py"

def run(case):
    tree = ROOT / "fixtures" / case / "docs" / "arc42"
    return subprocess.run([sys.executable, str(SCRIPT), str(tree)], capture_output=True, text=True)

def test_good_passes():
    assert run("output-good").returncode == 0

def test_bad_fails():
    r = run("output-bad")
    assert r.returncode == 1
    assert "front-matter" in r.stdout.lower() or "gap" in r.stdout.lower()

if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in [
        ("test_good_passes", test_good_passes),
        ("test_bad_fails", test_bad_fails),
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
    print(f"\n2 passed")
