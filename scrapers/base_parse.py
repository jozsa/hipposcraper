#!/usr/bin/env python2
"""Module for BaseParse"""
from scrapers import *


class BaseParse(object):
    """BaseParse class

    Contains read json data, and parsed html data for the scrapers
    to use. Also contains general methods to initialize the scrape.

    Args:
        link (str): link to the project page to scrape

    Attributes:
        json_data (dict): read json data from auth_data.json
        soup (obj): BeautifulSoup obj containing parsed link
        dir_name (str): directory name of the link
    """
    json_data = None
    soup = None
    dir_name = ""

    def __init__(self, link=""):
        self.htbn_link = link

    @property
    def htbn_link(self):
        return self.__htbn_link

    @htbn_link.setter
    def htbn_link(self, value):
        """Setter for htbn link

        Must contain holberton's url format for projects.

        Args:
            value (str): comes from argv[1] as the project link
        """
        valid_link = "intranet.hbtn.io/projects"
        while not (valid_link in value):
            print("[ERROR] Invalid link (must be to project on intranet.hbtn.io)")
            value = raw_input("Enter link to project: ")
        self.__htbn_link = value

    def get_json(self):
        """Method that reads auth_data.json.

        Sets json read to `json_data`
        """
        super_path = os.path.abspath("..")
        parent_path = os.path.basename(os.getcwd())
        with open("{}/{}/auth_data.json".format(super_path, parent_path), "r") as json_file:
            self.json_data = json.load(json_file)

    def get_soup(self):
        """Method that parses the `htbn_link` with BeautifulSoup

        Sets soup into self to create directories too.

        Returns:
            soup (obj): BeautifulSoup parsed html object
        """
        login = "https://intranet.hbtn.io/auth/sign_in"
        cj = cookielib.CookieJar()
        br = mechanize.Browser()

        sys.stdout.write("  -> Logging in... ")
        try:
            br.set_cookiejar(cj)
            br.open(login)
            br.select_form(nr=0)
            br.form['user[login]'] = self.json_data["intra_user_key"]
            br.form['user[password]'] = self.json_data["intra_pass_key"]
            br.submit()
            page = br.open(self.__htbn_link)
        except AttributeError:
            print("[ERROR] Login failed - are your auth_data credentials correct?")
            sys.exit()

        print("done")
        self.soup = BeautifulSoup(page, 'html.parser')
        return self.soup

    def find_directory(self):
        """Method that scrapes for project's directory name

        Sets project's directory's name to `dir_name`
        """
        find_dir = self.soup.find(string=re.compile("Directory: "))
        find_dir_text = find_dir.next_element.text
        self.dir_name = find_dir_text

    def create_directory(self):
        """Method that creates appropriate directory"""
        sys.stdout.write("  -> Creating directory... ")
        try:
            os.mkdir(self.dir_name)
            os.chdir(self.dir_name)
            print("done")
        except OSError:
            print("[ERROR] Failed to create directory - does it already exist?")
            sys.exit()

    def project_type_check(self):
        """Method that checks the project's type

        Checks for which scraper to use by scraping 'Github repository: '

        Returns:
            project (str): scraped project type
        """
        find_project = self.soup.find(string=re.compile("GitHub repository: "))
        project = find_project.next_sibling.text
        return project