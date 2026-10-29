#!/usr/bin/env bash
# arch-lint.sh — the one rule depguard cannot express: internal/<module> never imports another module's internal, and
# apps/<module> imports only its own module's internal. Exit 1 with the offending import on any violation. Run by `make arch-lint` (CI).
set -euo pipefail
MOD="bitbucket.org/ttec/humanifyos"
bad=0
for dir in apps internal; do
  for m in loom swatch rubric core app; do
    [ -d "$dir/$m" ] || continue
    while IFS= read -r line; do
      pkg="${line%%:*}"; imp="${line#*:}"
      other="${imp#$MOD/internal/}"; other="${other%%/*}"
      if [ "$other" != "$m" ]; then echo "arch-lint: $pkg imports $imp (module $m may not import internal/$other)"; bad=1; fi
    done < <(go list -f '{{$p := .ImportPath}}{{range .Imports}}{{$p}}:{{.}}{{"\n"}}{{end}}' "./$dir/$m/..." 2>/dev/null | grep -E "^[^:]+:$MOD/internal/" || true)
  done
done
while IFS= read -r line; do echo "arch-lint: $line (pkg/lib imports module code)"; bad=1; done < <(go list -f '{{$p := .ImportPath}}{{range .Imports}}{{$p}}:{{.}}{{"\n"}}{{end}}' ./pkg/lib/... 2>/dev/null | grep -E ":$MOD/(internal|apps)/" || true)
exit $bad
