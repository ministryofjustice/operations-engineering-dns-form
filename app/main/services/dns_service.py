import os
import yaml
import git
import logging
import shutil

logger = logging.getLogger(__name__)

class DNSService:
    def __init__(self):
        pass

    def clone_octodns_repo(self):
        repo_url = "https://github.com/ministryofjustice/dns.git"

        try:
            git.Repo.clone_from(repo_url, 'dns')
            logger.info("Octodns repository cloned successfully!")
        except Exception as e:
            logger.info("Error cloning octodns repository: %s", e)

    def get_fqdns_from_zone(self, file, hz):
        zone_data = yaml.safe_load(file)
        records = zone_data.keys()
        fqdns = []

        for record in records:
            if record != "":
                fqdns.append(record + "." + hz)
            else: 
                fqdns.append(hz)

        return fqdns

    def get_all_fqdns_from_zones(self):
        fqdns = []
        dir = "dns/hostedzones"

        for filename in os.listdir(dir):
            if filename.endswith('.yaml'):
                with open(os.path.join(dir, filename), 'r') as file:
                    hz = filename.removesuffix(".yaml")
                    fqdns = fqdns + self.get_fqdns_from_zone(file, hz)
        
        return fqdns
    
    def cleanup(self):
        shutil.rmtree("dns")

    def get_all_domains(self):
        self.clone_octodns_repo()

        domains = self.get_all_fqdns_from_zones()

        self.cleanup()

        return domains
