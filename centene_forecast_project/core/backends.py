from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from ldap3 import Server, Connection, ALL

class LDAPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            User = get_user_model()
            LDAP_Server_URI = "ldap://americas.global.nttdata.com"
            # LDAP_Server_URI = "ldap://ldpdmzprxy.nttdataservices.com"
            Bind_DN = f'AMERICAS\\{username}'  # Replace With A Valid Bind DN
            Bind_Password = password  # Replace With The Bind User's Password

            #LDAP Server Configuration
            SRVR = Server(LDAP_Server_URI, get_info=ALL)        
            connection = Connection(SRVR, user=Bind_DN, password=Bind_Password, auto_bind=True)

            # Bind to the LDAP server
            if not connection.bind():
                print('Not Binded')
                return messages.error('Bind Error')  # Authentication failed

            # Customize the following based on your LDAP structure
            # Retrieve additional user information from LDAP if needed
            base_dn = 'OU=Employees,DC=AMERICAS,DC=GLOBAL,DC=NTTDATA,DC=COM'
            search_filter = '(&(objectclass=person)(sAMAccountName={id}))'.format(id=username)

            connection.search(base_dn, search_filter, attributes=['CN','givenName','sn','mail'])
            # print(connection.entries)
            
            if len(connection.entries) == 1:
                entry = connection.entries[0]

                # print(entry)

                # Access LDAP attributes
                username = entry.CN.value
                first_name = entry.givenName.value
                last_name = entry.sn.value
                email = entry.mail.value

                # Print or use the retrieved attributes as needed
                print(f'Username: {username}')
                print(f'First Name: {first_name}')
                print(f'Last Name: {last_name}')
                print(f'Email: {email}')

            user_info = {
                'username': username,
                'first_name': first_name,  # Retrieve from LDAP attributes
                'last_name': last_name,   # Retrieve from LDAP attributes
                'email': email,  # Retrieve from LDAP attributes
            }

            # Create or retrieve the Django User object
            user, created = User.objects.get_or_create(username=username, defaults=user_info)

            return user

        except Exception as e:
            # Handle exceptions (e.g., connection error, LDAP server not available)
            # return messages.error(request,e)
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None