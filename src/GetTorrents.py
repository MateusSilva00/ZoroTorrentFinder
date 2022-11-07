from urllib.request import Request, urlopen
from urllib.error import HTTPError
from logger_conf import logger
from unidecode import unidecode
from bs4 import BeautifulSoup
import os, sys, subprocess


class GetTorrents:
    def __init__(self, search_term: str, providers_links: list) -> None:
        self.search_term = unidecode(search_term)
        self.providers = providers_links

    def format_link(self, provider_link: str) -> str:
        """
        Recieve a term and a provider to format a link
        """
        term_more_sign: str = self.search_term.replace(" ", "+")
        term_percentage_sign: str = self.search_term.replace(" ", "%20")

        if "MORE_SIGN" in provider_link:
            link = provider_link.replace("MORE_SIGN", term_more_sign)
        else:
            link = provider_link.replace("PERCENTAGE_SIGN", term_percentage_sign)

        return link

    def get_torrent_info(self, provider: str, page_source: BeautifulSoup) -> list:

        torrents_info: list = []

        count = 0

        if "torrentgalaxy.to" in provider:
            torrents = page_source.find_all("div", {"class": "tgxtablerow txlight"})
            for torrent in torrents:
                magnet = torrent.find("i", {"title": "magnet download"})
                magnet = magnet.find_parent("a", href=True)

                downloads = torrent.find("span", {"title": "Views"}).get_text(
                    strip=True
                )

                size = torrent.find("span", {"class": "badge-secondary"}).get_text(
                    strip=True
                )

                s_l = torrent.find("span", {"title": "Seeders/Leechers"}).get_text(
                    strip=True
                )
                s_l = s_l.replace("[", "").replace("]", "")
                seeders, leechers = s_l.split("/")

                updated_data = torrent.find_all("small")[1]
                updated_data = updated_data.get_text(strip=True)

                torrents_info.append(
                    [magnet["href"], downloads, size, seeders, leechers, updated_data]
                )

                count += 1

                if count >= 10:
                    break

        return torrents_info

    def get_list_torrents(self) -> list:
        """
        It receives a provider and a term to be searched. Will make a request to the site and return
        the torrents that were found
        """
        torrents = []
        for provider in self.providers:
            try:
                link = self.format_link(provider_link=provider)

                request = Request(link)
                webpage = urlopen(request).read()
                soup = BeautifulSoup(webpage, "html.parser")

                logger.debug(f"Requesting for {link}")

                infos = self.get_torrent_info(provider, soup)
                torrents.extend(infos)

            except HTTPError as e:
                logger.exception(f"Error in requisition {link} - {e.reason}")

            except Exception as e:
                logger.exception(f"Error not threat properly {e}")

        return torrents

    def get_torrent_metadata(self, torrents: list) -> list:
        metadata = []
        for torrent in torrents:
            try:
                magnet_link = torrent[0]
                torrent_name = torrent[0]
                torrent_name = torrent_name.split("dn=")[1]
                torrent_name = torrent_name.split("tr=")[0]

                torrent_name = torrent_name.replace("Bitsearch.to", "")
                torrent_name = torrent_name.replace("%5D", "")
                torrent_name = torrent_name.replace("%5B", "")

                torrent_name = torrent_name.replace("+", " ")
                torrent_name = torrent_name.replace(".", " ")

                downloads = int(torrent[1])
                size = torrent[2]
                seeders = int(torrent[3])
                leechers = int(torrent[4])
                updated_data = torrent[5]

                metadata.append(
                    [
                        torrent_name,
                        magnet_link,
                        downloads,
                        size,
                        seeders,
                        leechers,
                        updated_data,
                    ]
                )

            except Exception as e:
                logger.exception("Error not threat properly ", e)

        return metadata


if __name__ == "__main__":
    providers = []
    # providers.append("https://solidtorrents.to/search?q=MORE_SIGN")
    providers.append("https://torrentgalaxy.to/torrents.php?search=MORE_SIGN#results")
    # providers.append("https://tpb.party/search/PERCENTAGE_SIGN/1/99/0")

    search_term = input("Digite o nome do filme/livro no qual você deixa buscar: ")

    gt = GetTorrents(search_term=search_term, providers_links=providers)
    torrents = gt.get_list_torrents()
    handlers = gt.get_torrent_metadata(torrents)

    # print(torrents)

    for idx in range(0, len(handlers)):
        print(
            f"{idx} - {handlers[idx][0]} - {handlers[idx][2]} downloads - {handlers[idx][3]} size"
        )

    baixar = int(input("Qual torrent deixa baixar: "))
    magnet = handlers[baixar][1]

    if sys.platform.startswith("linux"):
        subprocess.Popen(
            ["xdg-open", magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    elif sys.platform.startswith("win32"):
        os.startfile(magnet)
