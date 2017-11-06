class ArosiaCache:
    # TODO: Implement an actual persistent cache, shared with other agents
    def add_contact(self, arosia_id: str, lora_id: str):
        self.CONTACT_MAP[arosia_id] = lora_id

    def get_contact(self, arosia_id: str):
        return self.CONTACT_MAP.get(arosia_id)

    def add_account(self, arosia_id: str, lora_id: str):
        self.ACCOUNT_MAP[arosia_id] = lora_id

    def get_account(self, arosia_id: str):
        return self.ACCOUNT_MAP.get(arosia_id)

    def add_product(self, arosia_id: str, lora_id: str):
        product_list = self.AFTALE_PRODUCT_MAP.setdefault(arosia_id, [])
        product_list.append(lora_id)

    def get_products(self, arosia_id: str):
        return self.AFTALE_PRODUCT_MAP.get(arosia_id)

    def __init__(self):
        # Contains a map of Arosia Contact UUIDs to LoRa bruger and organisation
        # UUIDs
        self.CONTACT_MAP = {}
        # Contains a map of Arosia Account UUIDs to LoRa interessefællesskab
        # UUIDs
        self.ACCOUNT_MAP = {}
        # Contains a map of Arosia Kundeaftale UUIDs to a list of their
        # associated # products as LoRa Klasse UUIDs
        self.AFTALE_PRODUCT_MAP = {}
