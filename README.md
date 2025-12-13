# ✅ faneX-ID Integration Validation Action

> A **GitHub Composite Action** to ensure quality and compatibility of faneX-ID extensions. 🛡️

Use this action in your CI pipeline to auto-validate your `manifest.json`, folder structure, and Core version compatibility.

---

## 🚀 Usage

In your repository's `.github/workflows/ci.yml`:

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: faneX-ID/integration-validation@main
        with:
          # Optional: Target a specific core version for compatibility checks 🎯
          core_version: "0.1.0"
```

## 🔍 What it Checks
1.  **JSON Syntax** 📄 — Validates `addons.json` and `manifest.json`.
2.  **Manifest Schema** 📐 — Ensures `domain`, `name`, `version`, and `implementations` exist.
3.  **Domain Validity** 🆔 — Checks for unique, valid identifiers.
4.  **File Existence** 📁 — Verifies that referenced `integration.py` or `.ps1` files exist.
5.  **Version Compatibility** 🤝 — Ensures `min_core_version` is met.

## 🛠️ Development
This action wraps the `validate.py` script provided by the faneX-ID Core team.

## 📝 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.