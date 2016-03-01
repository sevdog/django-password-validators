.PHONY: test translatte

test:
	tox
  
translatte:
	cd ./django_password_validators; django-admin.py makemessages -a
	cd ./django_password_validators; django-admin.py compilemessages 
	
new_version_major:
	bumpversion major
	
new_version_minor:
	bumpversion minor
	
new_version_patch:
	bumpversion path

testrelease:
	python setup.py sdist bdist bdist_wheel upload -r test

release:
	python setup.py sdist bdist bdist_wheel upload
