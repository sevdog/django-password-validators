.PHONY: test translatte new_version_major new_version_minor new_version_patch release

test:
	tox
  
translatte:
	cd ./django_password_validators; django-admin.py makemessages -a
	cd ./django_password_validators; django-admin.py compilemessages -f
	
new_version_major:
	bumpversion major
	
new_version_minor:
	bumpversion minor
	
new_version_patch:
	bumpversion patch

release:
    rm -r dist/
    python -m build
    twine check dist/*
    twine upload dist/*
	git push --tags

