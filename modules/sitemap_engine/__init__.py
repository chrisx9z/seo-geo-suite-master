# -*- coding: utf-8 -*-
from .news_sitemap import NewsSitemapGenerator
from .sitemap_checker import check_sitemap

NewsSitemapEngine = NewsSitemapGenerator
__all__ = ['NewsSitemapGenerator', 'NewsSitemapEngine', 'check_sitemap']
