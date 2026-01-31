# modules/base.py
from abc import ABC, abstractmethod


class BaseSite(ABC):
    @abstractmethod
    def pode_processar(self, url: str) -> bool:
        """Retorna True se este módulo suporta a URL passada."""
        pass

    @abstractmethod
    def get_titulo(self, url: str) -> str:
        """Retorna o nome da obra (anime/filme) para criar a pasta."""
        pass

    @abstractmethod
    def get_conteudo(self, url: str):
        """
        Retorna uma lista de itens para baixar.
        Ex: [{'numero': '01', 'url': 'http...'}, {'numero': '02' ...}]
        """
        pass

    @abstractmethod
    def get_links_download(self, url_conteudo: str) -> dict:
        """
        Recebe o link de um episódio/filme e retorna os links diretos do vídeo.
        Ex: {'F-HD': 'http://video.mp4', 'SD': '...'}
        """
        pass
