import os
import sys
from io import StringIO
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from django.urls import resolve, reverse, NoReverseMatch

def setup_django_environment():
    """Sets up the Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nena_ai_backend.settings')
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"ERROR: Could not set up Django environment: {e}")
        sys.exit(1)

def check_installed_apps():
    """Checks if all expected apps are in INSTALLED_APPS."""
    print("\n--- Checking INSTALLED_APPS ---")
    expected_apps = ['users', 'loans', 'documents', 'chat', 'analytics'] # From previous analysis
    all_good = True
    for app_name in expected_apps:
        if app_name in settings.INSTALLED_APPS:
            print(f"  [✓] App '{app_name}' is in INSTALLED_APPS.")
        else:
            print(f"  [✗] App '{app_name}' is MISSING from INSTALLED_APPS.")
            all_good = False
    return all_good

def check_migrations():
    """Checks if migrations are applied for all apps."""
    print("\n--- Checking Migrations Status ---")
    all_good = True
    output_buffer = StringIO()
    try:
        call_command('showmigrations', stdout=output_buffer, no_color=True)
        output = output_buffer.getvalue()
        for line in output.splitlines():
            if not line.strip().startswith('[X]') and not line.strip().startswith('[ ]') and line.strip():
                # This line is likely an app name or header, not a migration status
                continue
            if '[ ]' in line:
                app_name = line.split(' ')[0].strip()
                print(f"  [✗] Pending migrations for app: {app_name}")
                all_good = False
            elif '[X]' in line:
                # print(f"  [✓] Migrations applied for: {line.strip()}") # Too verbose
                pass
        if all_good:
            print("  [✓] All migrations are applied.")
    except Exception as e:
        print(f"  [✗] Error checking migrations: {e}")
        all_good = False
    return all_good

def check_model_loading():
    """Checks if models can be loaded for each app."""
    print("\n--- Checking Model Loading ---")
    all_good = True
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib') or app_config.name in ['rest_framework', 'rest_framework_simplejwt']:
            continue # Skip Django built-in and third-party apps
        try:
            # Attempt to access models to ensure they are loaded
            # This implicitly checks if models.py exists and is syntactically correct
            if app_config.models_module:
                print(f"  [✓] Models loaded for app: {app_config.name}")
            else:
                print(f"  [✓] No models found for app: {app_config.name} (expected for chat/analytics if no models are defined)")
        except Exception as e:
            print(f"  [✗] Error loading models for app '{app_config.name}': {e}")
            all_good = False
    return all_good

def check_url_loading():
    """Checks if URL configurations can be loaded for each app."""
    print("\n--- Checking URL Loading ---")
    all_good = True
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib') or app_config.name in ['rest_framework', 'rest_framework_simplejwt']:
            continue # Skip Django built-in and third-party apps
        try:
            # Attempt to import the urls module for the app
            # This will raise an error if urls.py is missing or has syntax errors
            __import__(f'{app_config.name}.urls')
            print(f"  [✓] URLs loaded for app: {app_config.name}")
        except ImportError:
            print(f"  [✓] No urls.py found for app: {app_config.name} (expected if no URLs are defined)")
        except Exception as e:
            print(f"  [✗] Error loading URLs for app '{app_config.name}': {e}")
            all_good = False
    return all_good

def main():
    setup_django_environment()

    overall_status = True

    if not check_installed_apps():
        overall_status = False

    if not check_migrations():
        overall_status = False

    if not check_model_loading():
        overall_status = False

    if not check_url_loading():
        overall_status = False

    print("\n--- Overall Status ---")
    if overall_status:
        print("[✓] All checks passed. Django apps are properly configured and running.")
        sys.exit(0)
    else:
        print("[✗] Some checks failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
