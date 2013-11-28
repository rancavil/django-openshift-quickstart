#!/usr/bin/env python
import hashlib, imp, os, sqlite3, sys

# Load the openshift helper library
lib_path      = os.environ['OPENSHIFT_REPO_DIR'] + 'wsgi/openshift/'
modinfo       = imp.find_module('openshiftlibs', [lib_path])
openshiftlibs = imp.load_module('openshiftlibs', modinfo[0], modinfo[1], modinfo[2])

# Open the database
conn = sqlite3.connect(os.environ['OPENSHIFT_DATA_DIR'] + '/db.sqlite3')
c    = conn.cursor()

# Grab the default security info
c.execute('SELECT password FROM AUTH_USER WHERE id = 1')
pw_info = c.fetchone()[0]

# The password is stored as [hashtype]$[iterations]$[salt]$[hashed]
pw_fields = pw_info.split("$")
hashtype  = pw_fields[0]
old_salt  = pw_fields[2]
old_pass  = pw_fields[3]

# Randomly generate a new password and a new salt
# The PASSWORD value below just sets the length (12)
# for the real new password.
old_keys = { 'SALT': old_salt, 'PASS': '123456789ABC' }
use_keys = openshiftlibs.openshift_secure(old_keys)

# Encrypt the new password
new_salt = use_keys['SALT']
new_pass = use_keys['PASS']

c.close()
conn.close()

# Update the user admin password
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'wsgi', 'openshift'))
from django.contrib.auth.models import User
usr = User.objects.get(username__exact='admin')
usr.set_password(new_pass)
usr.save()

# Print the new password info
print "Django application credentials:\n\tuser: admin\n\t" + new_pass
