import os
import yaml
import git
import logging

logger = logging.getLogger(__name__)

class DNSService:
    def __init__(self):
        pass

    def clone_octodns_repo(self):
        repo_url = "https://github.com/ministryofjustice/dns.git"

        try:
            git.Repo.clone_from(repo_url, '.')
            logger.info("Octodns repository cloned successfully!")
        except Exception as e:
            logger.info("Error cloning octodns repository: %s", e)

    def get_fqdn_from_zone(self, file):
        fqdns = []
        zone_data = yaml.safe_load(file)

        for record in zone_data.get('records', []):
            fqdn = record.get('fqdn', None)
            if fqdn:
                fqdns.append(fqdn)

        return fqdns

    def get_all_fqdns_from_zones(self):
        fqdns = []
        
        for filename in os.listdir("./dns/hostedzones"):
            if filename.endswith('.yaml'):
                with open(os.path.join(dir, filename), 'r') as file:
                    fqdns = fqdns + self.get_fqdn_from_zone(file)
        
        return fqdns

    def get_all_domains(self):
        self.clone_octodns_repo()

        return self.get_all_fqdns_from_zones()
