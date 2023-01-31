from . import auth

from gql import gql, Client
from gql.dsl import DSLSchema, DSLQuery, dsl_gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.websockets import WebsocketsTransport

# for file schema support
from graphql import DocumentNode, Source, parse
from graphql.utilities import get_operation_ast
import os

ANDERSEN_GRAPHQL_PROD = 'https://graphql.andersen-ev.com'
ANDERSEN_GRAPHQL_WS   = 'wss://graphql.andersen-ev.com/graphql'

class AndersenA2:
    def __init__(self):
        
        self.gqclient = None
        self.wsclient = None

        # load the graphql schema as a DocumentNode
        spath = os.path.join(os.path.dirname(__file__), "schema/andersen.graphql")
        schema = open(spath, 'r').read()        
        self._docnode = parse(Source(schema), "GraphQL request")
    
    def _get_query(self, name):
      # search the DocumentNode for the query definition with the given name
      # this is a bit of a bodge but it lets us nicely separate the code from the schema
      # query = get_operation_ast(self._docnode, name)
      query = next((d for d in self._docnode.definitions if d.name.value == name), None)      
      return query

    def _get_operation(self, query):
      # find the operation name for the given query
      qss = next((s for s in query.selection_set.selections if s.name.kind == 'name'), None)
      return qss.name.value

    def _execute_query(self, name, variable_values = None):

      assert self.gqclient, "GraphQL client must be instantiated"

      query  = self._get_query(name)
      opname = self._get_operation(query)

      result = self.gqclient.execute(
        query, 
        variable_values = variable_values
      )
      try:
        return result[opname]
      except:
        print(result)
        raise
        return None

    def _subscribe(self, name, variable_values = None):
      
      assert self.wsclient, "Websocket client must be instantiated"
      query = self._get_query(name)

      return self.wsclient.subscribe(
        query,
        variable_values = variable_values
      )



    def authenticate(self, email, password):
        """ Authenticate with the AndersenEV cloud API
        Args:
            email(str): Email address used to register with the Konnect+ app
            password(str)
        Returns:
            id_token(str): Access token returned by AWS Cognito service 
        """  

        #
        # Authentication requires that we authenticate
        # using the AWS Cognito service. The ID token must be
        # used for subsequent calls to the Andersen graphql API
        #        
        aa = auth.AndersenAuth()
        self.id_token = aa.authenticate(email, password)
        
        headers = { "Authorization": f"Bearer {self.id_token}" }
        transport = RequestsHTTPTransport(url=ANDERSEN_GRAPHQL_PROD, verify=True, retries=3, headers=headers)        
        self.gqclient = Client(transport=transport)

        return self.id_token

    def confirm_device(self, deviceName):
        raise NotImplementedError
        #self.gqclient.confirm_device(deviceName) 
        pass

    def get_support_message(self):
        return self._execute_query("getSupportMessage")

    def get_current_user_devices(self):
        return self._execute_query("getCurrentUserDevices")

    def get_device(self, deviceId):
        return self._execute_query("getDevice", variable_values={'id': deviceId})

    def get_device_status(self, deviceId):
        return self._execute_query("getDeviceStatusSimple", variable_values={'id':deviceId})

    def get_device_charge_rates(self, deviceId):
        return self._execute_query("getDeviceChargeRates", variable_values={'id': deviceId})

    def get_device_lora(self, deviceId):
        return self._execute_query("getDeviceLora", variable_values={'id': deviceId})

    def get_device_solar(self, deviceId):
        return self._execute_query("getDeviceSolar", variable_values={'id': deviceId})

    def get_device_solar_binned(self, deviceId):
        return self._execute_query("getDeviceSolarBinned", 
          variable_values = {
          'id': deviceId
        })

    def search_address(self, addressFragment, countryCode):
        return self._execute_query("searchAddress", 
          variable_values = {
            'addressFragment': addressFragment, 
            'countryCode': countryCode
          }
        )     

    def get_device_calculated_charge_logs(self, deviceId):
        return self._execute_query("getDeviceCalculatedChargeLogs", 
          variable_values={'id': deviceId
        })

    def set_charge_rate(self, chargeId):
        return self._execute_query("updateChargeRate", 
          variable_values={
            'id': chargeId
        })         

    def set_schedule_names(self, deviceId):
        return self._execute_query("setScheduleNames", 
          variable_values = {
            'id': deviceId,
            # missing params
        })

    def create_charge_rate(self):
        return self._execute_query("createChargeRate", 
          variable_values = {
            'id': deviceId
          })

    def unclaim_device(self, deviceId):
        return self._execute_query("unclaimDevice", 
          variable_values = { 'deviceId': deviceId
        })

    def run_aev_command(self, deviceId, functionName, paramString=None):
        return self._execute_query("runAEVCommand", 
          variable_values={
            'deviceId': deviceId, 
            'functionName': functionName,
            'params': paramString
          }
        )    

    def user_lock(self, deviceId):
        # disables charging
        return self.run_aev_command(deviceId, "userLock")

    def user_unlock(self, deviceId):
        # enables charging
        return self.run_aev_command(deviceId, "userUnlock")

    def upsert_account(self, firstName, lastName):
        return self._execute_query("upsertAccount", 
          variable_values={
            'firstName': firstName, 
            'lastName': lastName
        })         

    def set_schedules(self, deviceId, slots):
        return self._execute_query("setSchedules", 
          variable_values={
            'deviceId': deviceId, 
            'scheduleSlots': slots
          })  

    def get_schedule(self, deviceId, slotNumber):
      result = self.get_device(deviceId)
      return result['deviceStatus']['scheduleSlotsArray'][slotNumber]
      
    def enable_schedule(self, deviceId, slotNumber, enabled=True):
      schedule = self.get_schedule(deviceId, slotNumber)
      schedule['enabled'] = enabled
      slots = { f'sch{slotNumber}': schedule }
      return self.set_schedules(deviceId, slots=slots )

    def create_schedule(self, deviceId, slotNumber, schedule=None):
      if not schedule:
        schedule = {
          'startHour': 0,
          'startMinute': 30,
          'endHour': 4,
          'endMinute': 30,
          'enabled': True,
          "dayMap": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": True,
            "sunday": True
          }                
        }

      slots = { f'sch{slotNumber}': schedule }
      return self.set_schedules(deviceId, slots)

    def delete_charge_rate(self, chargeId):
        return self._execute_query("deleteChargeRate", 
          variable_values={
            'id': chargeId
          })         

    def upsert_device_friendly_name(self, deviceId, friendlyName):
        return self._execute_query("upsertDeviceFriendlyName", 
          variable_values={
            'deviceId': deviceId, 
            'friendlyName': friendlyName
          })

    def get_solar(self, deviceId):
        return self._execute_query("getSolar", 
          variable_values={
            'deviceId': deviceId
          })        
        
    def set_solar(self, deviceId, override=False, chargeAlways=False, maxGridChargePercent=10):
        return self._execute_query("setSolar", 
          variable_values={
            'deviceId': deviceId, 
            'override': override,
            'chargeAlways': chargeAlways,
            'maxGridChargePercent': maxGridChargePercent
          })         

    def register_mobile_device(self, c2dmToken):
        # token: returned from the goodle C2DM register device API:
        # https://android.apis.google.com/c2dm/register3
        # probably unnecessary unless device push notifications are required
        # and we are running on Android
        return self._execute_query("registerMobileDevice", 
          variable_values={
            'token': c2dmToken
          })         

    def unregister_mobile_device(self, c2dmToken):
        return self._execute_query("unregisterMobileDevice", 
          variable_values={
            'token': c2dmToken
          })         

    def set_all_schedules_disabled(self, deviceId):
        # disables all schedules and puts the charger into 'ready' (unlocked) state
        return self._execute_query("setAllSchedulesDisabled", 
          variable_values={
            'deviceId': deviceId
          })         

    def claim_device_by_name(self, deviceName):
        return self._execute_query("claimDeviceByName", 
          variable_values={
            'deviceName': deviceName
          })         

    def device_by_name(self, name):
      for device in self.get_current_user_devices():
        if device['deviceInfo']['friendlyName'] == name:
          return device

    def device_id_from_name(self, name):
      return self.device_by_name(name)['id']

    def subscribe_device_updates(self, deviceId):        
      if not self.wsclient:
        transport = WebsocketsTransport(
            url=ANDERSEN_GRAPHQL_WS, 
            init_payload={'authToken': f"Bearer {self.id_token}"}
            )

        self.wsclient =  Client(
            transport=transport,
            fetch_schema_from_transport=False
        )

      return self._subscribe('deviceStatusUpdated', variable_values={'id': deviceId} )
