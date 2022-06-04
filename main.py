import requests
import uuid

class AuthInfo:
   netSession  : requests.Session   = None
   authUuid    : str                = None
   authToken   : str                = None
   username    : str                = None
   password    : str                = None
   auth2fa     : str                = None

def generateAuthUUID():
   return uuid.uuid4().hex[0:21] # vk requires uuid with 21 character

def makeInitialRequest(authInfo: AuthInfo):
   # in <script> contains auth token and we need it
   response = authInfo.netSession.get(
      "https://id.vk.com/auth",
      params={
         "app_id": 7913379,
         "redirect_uri": "https://vk.com/im",
         "v": "1.46.0",
         "uuid": authInfo.authUuid,
         "scope": 404634839,
         "action": "eyJuYW1lIjoibm9fcGFzc3dvcmRfZmxvdyIsInBhcmFtcyI6eyJ0eXBlIjoic2lnbl9pbiJ9fQ=="
      }
   )

   assert response.status_code == 200

   idx = response.text.find("auth_token")
   authInfo.authToken = response.text[idx+13:idx+208]

def tryAutorize(authInfo: AuthInfo):
   response = authInfo.netSession.post(
      "https://login.vk.com/",
      params={
         "act": "connect_authorize"
      },
      data={
         "username": authInfo.username,
         "password": authInfo.password,
         "auth_token": authInfo.authToken,
         "sid": "",
         "uuid": authInfo.authUuid,
         "v": "5.174",
         "device_id": "WQmxgMsMTU2WlQPpYTvt6", # idk what it's mean, but WQmxgMsMTU2WlQPpYTvt6 maybe means PC
         "service_group": "",
         "version": 1,
         "app_id": 7913379,
         "code_2fa": authInfo.auth2fa
      },
      headers={
         "origin": "https://id.vk.com",
         "referer": "https://id.vk.com/",
         "Host": None
      }
   )
   return response.json()

def saveToken(response: dict, fileName: str):
   with open(fileName, "w+") as f:
      f.write(response['data']['access_token'])
      f.close()

def main():
   authInfo = AuthInfo()
   
   authInfo.netSession = requests.Session()
   authInfo.authUuid = generateAuthUUID()

   print("Authorization UUID: " + authInfo.authUuid)

   makeInitialRequest(authInfo) # make initial get request to id.vk.com/auth

   authInfo.username = input("Enter username(number, with country code and +): ")
   authInfo.password = input("Enter password: ")

   while True:
      response = tryAutorize(authInfo)

      if response['type'] != 'okay':
         print("Can't autorize: " + response['error_info'])
         return 1

      match response['data']['response_type']:
         case 'need_2fa':
            authInfo.auth2fa = input("Enter 2FA code: ")
            continue # try authorize again but with 2fa code
         case 'auth_token':
            # we have result now
            saveToken(response, "token")
            print(response)
            print("Authorization successfuly. Token is contained in file 'token'")
            return 0
         case _:
            print("Unknown error: " + str(response))
            return 1
   return -1 # we shouldn't get here
   
if __name__ == "__main__":
   exit(main())