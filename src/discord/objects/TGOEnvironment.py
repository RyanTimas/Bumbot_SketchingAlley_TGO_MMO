import pytz


class TGOEnvironment:
    def __init__(self, environment_id: int, name: str, variant_name: str, dex_no: int, variant_no: int, location: str, description: str, img_root: str, is_night_environment: bool, in_circulation: bool, encounter_rate: int):
        self.environment_id = environment_id

        self.name = name
        self.variant_name = variant_name
        self.dex_no = dex_no
        self.variant_no = variant_no

        self.location = location
        self.description = description

        self.short_name = img_root
        self.img_root = img_root + f'_{variant_no}'
        self.is_night_environment = is_night_environment == 1
        self.in_circulation = in_circulation

        self.encounter_rate = encounter_rate
        self.timezone = pytz.timezone('US/Eastern')

NATIONAL_ENV = TGOEnvironment(environment_id=0, name='National Encyclopedia', variant_name='', dex_no=0, variant_no=0, location='Global', description='', img_root='national_env', is_night_environment=False, in_circulation=False, encounter_rate=0)

TEST_ENV = TGOEnvironment(environment_id=1, name='Test Environment - Forest', variant_name='Summer - Day', dex_no=1, variant_no=1, location='Eastern United States', description='', img_root='forest_est', is_night_environment=False, in_circulation=True, encounter_rate=5)
TEST_SPAWN_POOL = [TEST_ENV]