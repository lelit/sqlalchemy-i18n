from pytest import raises
from sqlalchemy_i18n import UnknownLocaleError
from tests import TestCase


class TestTranslationMapping(TestCase):
    def test_proxy_contains(self):
        article = self.Article()
        article.translations['en']
        assert 'en' in article.translations

    def test_translation_mapping_attribute_getter(self):
        article = self.Article()
        article.translations.en.name = 'Something'
        assert article.name == 'Something'

    def test_attribute_accessor_for_unknown_locale(self):
        with raises(UnknownLocaleError):
            self.Article.translations.some_unknown_locale

    def test_proxy_not_contains(self):
        article = self.Article()
        assert 'unknown_locale' not in article.translations

    def test_items(self):
        article = self.create_article()
        assert isinstance(article.translations.items(), list)

    def test_set_item(self):
        article = self.create_article()
        self.session.expunge_all()
        article = self.session.query(self.Article).first()
        locale_obj = self.Article.__translatable__['class'](
            name=u'Some other thing'
        )
        article.translations['en'] = locale_obj
        self.session.commit()
        self.session.expunge_all()
        article = self.session.query(self.Article).first()

        assert article.translations['en'].name == u'Some other thing'
