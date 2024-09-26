import os
import yaml
import git
import logging
import shutil

logger = logging.getLogger(__name__)

class DNSService:
    def __init__(self):
        self.dns_repo = "https://github.com/ministryofjustice/dns.git"
        self.temporary_directory = "/tmp"
        self.dns_repo_dir = self.temporary_directory + "/dns"
        self.hz_dir = self.dns_repo_dir + "/hostedzones"

    def clone_octodns_repo(self):
        try:
            if not os.path.isdir(self.temporary_directory):
                os.mkdir(self.temporary_directory)

            if not os.path.isdir(self.dns_repo_dir):
                git.Repo.clone_from(self.dns_repo, self.dns_repo_dir)
                logger.info("Octodns repository cloned successfully!")
        except Exception as e:
            logger.info("Error cloning octodns repository: %s", e)

    def get_fqdns_from_zone(self, zone_data, hz):
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

        for filename in os.listdir(self.hz_dir):
            if filename.endswith('.yaml'):
                with open(os.path.join(self.hz_dir, filename), 'r') as file:
                    hz = filename.removesuffix(".yaml")
                    zone_data = yaml.safe_load(file)
                    fqdns = fqdns + self.get_fqdns_from_zone(zone_data, hz)
        
        return fqdns
    
    def cleanup(self):
        if os.path.isdir(self.hz_dir):
            shutil.rmtree(self.dns_repo_dir)

    def get_all_domains(self):
        self.clone_octodns_repo()

        domains = self.get_all_fqdns_from_zones()

        self.cleanup()

        return domains