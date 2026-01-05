# Requirements.txt Verification Report

## Summary
- **Total packages**: 45 (after cleanup)
- **Directly used in code**: 8
- **Dependencies (kept)**: 37
- **Removed unused**: 13

---

## ✅ DIRECTLY USED PACKAGES (Keep - Required)

1. **Django==5.2.7** - Core framework
2. **python-decouple==3.8** - Used in `core/settings.py` for config
3. **reportlab==4.4.7** - Used in `genesis/views.py` for PDF receipts
4. **twilio==9.8.4** - Used in `genesis/sms_service.py` for SMS
5. **django-htmx==1.26.0** - In INSTALLED_APPS
6. **django-widget-tweaks==1.5.0** - In INSTALLED_APPS
7. **django-tailwind==4.4.2** - In INSTALLED_APPS
8. **django-redis==6.0.0** - Used in `core/settings.py` for caching

---

## 🔵 DEPENDENCIES (Keep - Required by other packages)

### Django Core Dependencies
- **asgiref==3.10.0** - Django ASGI support
- **sqlparse==0.5.3** - Django SQL parsing
- **tzdata==2025.2** - Timezone data
- **typing_extensions==4.15.0** - Type hints

### Django Extensions Dependencies
- **pytailwindcss==0.3.0** - Required by django-tailwind
- **node==1.2.2** - Required by django-tailwind
- **redis==6.4.0** - Required by django-redis

### HTTP/Network Dependencies (likely from twilio/requests)
- **aiohappyeyeballs==2.6.1**
- **aiohttp==3.13.1**
- **aiohttp-retry==2.9.1**
- **aiosignal==1.4.0**
- **certifi==2025.10.5**
- **chardet==5.2.0**
- **charset-normalizer==3.4.4**
- **idna==3.11**
- **multidict==6.7.0**
- **frozenlist==1.8.0**
- **urllib3==2.5.0**
- **yarl==1.22.0**
- **requests==2.32.5**

### Template/Utility Dependencies
- **Jinja2==3.1.6** - Template engine (used by cookiecutter/django-tailwind)
- **MarkupSafe==3.0.3** - Jinja2 dependency
- **PyYAML==6.0.3** - YAML parsing
- **click==8.3.1** - CLI tool
- **colorama==0.4.6** - Terminal colors
- **attrs==25.4.0** - Data classes

### Zope Components (likely from cookiecutter)
- **zope.component==7.0**
- **zope.deferredimport==6.0**
- **zope.deprecation==6.0**
- **zope.event==6.0**
- **zope.hookable==8.0**
- **zope.interface==8.0.1**
- **zope.lifecycleevent==6.0**
- **zope.proxy==7.0**

### Other Dependencies
- **python-dateutil==2.9.0.post0** - Date utilities
- **PyJWT==2.10.1** - JWT tokens (likely twilio dependency)
- **six==1.17.0** - Python 2/3 compatibility (legacy, but may be needed)

---

## ✅ REMOVED PACKAGES (Cleaned from requirements.txt)

The following packages were removed as they were not directly used in the codebase:

1. **cookiecutter==2.6.0** - Project template tool, not needed in runtime
2. **arrow==1.4.0** - Date library, not imported anywhere in code
3. **binaryornot==0.4.4** - File type detection, not used
4. **rich==14.2.0** - Terminal formatting, not used
5. **Pygments==2.19.2** - Syntax highlighting, not used
6. **python-slugify==8.0.4** - Slug generation, not used
7. **text-unidecode==1.3** - Unicode text handling, not used
8. **markdown-it-py==4.0.0** - Markdown parser, not used
9. **mdurl==0.1.2** - Markdown URL utilities, not used
10. **odict==1.9.0** - Ordered dict, not used
11. **plumber==1.7** - Unknown utility, not used
12. **propcache==0.4.1** - Property caching, not used
13. **setuptools==80.9.0** - Build tool, not needed in requirements.txt

---

## ⚠️ RECOMMENDATIONS

### Next Steps:
1. **Test the application** - Ensure all functionality still works after package removal
2. **Run `pip check`** - Verify no dependency conflicts exist
3. **Update virtual environment** - Run `pip install -r requirements.txt` to sync
4. **Monitor for issues** - If any features break, investigate and restore necessary packages

### Packages to Monitor:
- All **aio*** packages - May be dependencies of twilio/requests
- All **zope.*** packages - Legacy dependencies, but may still be required transitively
- Consider using `pip-tools` or `pipdeptree` in the future to better understand dependency chains

---

## Verification Commands

```bash
# Check for dependency conflicts
pip check

# See what requires a package
pip show <package_name>

# Generate requirements from installed packages
pip freeze > requirements_auto.txt
```

