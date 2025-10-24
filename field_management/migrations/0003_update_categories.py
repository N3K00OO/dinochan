from django.db import migrations


NEW_CATEGORY_DEFINITIONS = [
    ("padel", "Padel"),
    ("tennis", "Tennis"),
    ("badminton", "Badminton"),
    ("basket", "Basket"),
    ("sepak-bola", "Sepak Bola"),
    ("mini-soccer", "Mini Soccer"),
    ("futsal", "Futsal"),
    ("billiard", "Billiard"),
    ("tenis-meja", "Tenis Meja"),
    ("volly-ball", "Volly Ball"),
]

RENAMED_SLUGS = {
    "basketball": ("basket", "Basket"),
    "football": ("sepak-bola", "Sepak Bola"),
    "futsal": ("futsal", "Futsal"),
    "badminton": ("badminton", "Badminton"),
    "tennis": ("tennis", "Tennis"),
}


def update_categories(apps, schema_editor):
    Category = apps.get_model("field_management", "Category")

    for old_slug, (new_slug, new_name) in RENAMED_SLUGS.items():
        try:
            category = Category.objects.get(slug=old_slug)
        except Category.DoesNotExist:
            category = None

        if category is None:
            try:
                category = Category.objects.get(slug=new_slug)
            except Category.DoesNotExist:
                category = Category.objects.filter(name__iexact=new_name).first()

        if category is None:
            category = Category.objects.create(slug=new_slug, name=new_name)
            continue

        updated_fields = []
        if category.slug != new_slug:
            category.slug = new_slug
            updated_fields.append("slug")
        if category.name != new_name:
            category.name = new_name
            updated_fields.append("name")
        if updated_fields:
            category.save(update_fields=updated_fields)

    for slug, name in NEW_CATEGORY_DEFINITIONS:
        category, created = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        if not created and category.name != name:
            category.name = name
            category.save(update_fields=["name"])


def revert_categories(apps, schema_editor):
    Category = apps.get_model("field_management", "Category")

    added_slugs = {
        "padel",
        "mini-soccer",
        "billiard",
        "tenis-meja",
        "volly-ball",
    }
    Category.objects.filter(slug__in=added_slugs).delete()

    original_mappings = {
        "basket": ("basketball", "Basketball Courts"),
        "sepak-bola": ("football", "Football Fields"),
        "futsal": ("futsal", "Futsal Arenas"),
        "badminton": ("badminton", "Badminton Halls"),
        "tennis": ("tennis", "Tennis Courts"),
    }

    for current_slug, (old_slug, old_name) in original_mappings.items():
        try:
            category = Category.objects.get(slug=current_slug)
        except Category.DoesNotExist:
            continue

        updated_fields = []
        if category.slug != old_slug:
            category.slug = old_slug
            updated_fields.append("slug")
        if category.name != old_name:
            category.name = old_name
            updated_fields.append("name")
        if updated_fields:
            category.save(update_fields=updated_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("field_management", "0002_seed_default_categories"),
    ]

    operations = [
        migrations.RunPython(update_categories, revert_categories),
    ]
