.PHONY: test translatte new_version_major new_version_minor new_version_patch release

test:
	tox

translatte:
	cd ./django_password_validators; django-admin.py makemessages -a
	cd ./django_password_validators; django-admin.py compilemessages -f

new_version_major:
	bump-my-version major

new_version_minor:
	bump-my-version minor

new_version_patch:
	bump-my-version patch

release:
	rm -r dist/
	python -m build
	twine check dist/*
	twine upload dist/*
	git push --tags
