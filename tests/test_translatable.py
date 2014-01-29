from pytest import raises
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, UnknownLocaleError
from tests import TestCase


class TestTranslatableModel(TestCase):
    def test_auto_creates_relations(self):
        article = self.Article()
        assert article.translations

    def test_auto_creates_current_translation(self):
        article = self.Article()
        assert article.current_translation

    def test_translatable_attributes(self):
        article = self.Article()
        assert article.__translatable__['class']
        assert article.__translatable__['class'].__name__ == (
            'ArticleTranslation'
        )

    def test_relationship_consistency(self):
        article = self.Article()
        article.name = u'Some article'
        assert article.current_translation == article.translations['en']

    def test_translated_columns(self):
        article = self.Article()
        columns = article.__translatable__['class'].__table__.c
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns

    def test_property_delegators(self):
        article = self.Article()
        article.translations['en']

        assert not article.name
        article.current_translation.name = u'something'
        assert article.name == u'something'
        article.name = u'some other thing'
        assert article.current_translation.name == u'some other thing'
        assert article.translations['en'].name == u'some other thing'

    def test_appends_locale_column_to_translation_table(self):
        table = self.Model.metadata.tables['article_translation']
        assert 'locale' in table.c

    def test_commit_session(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        article = self.session.query(self.Article).get(1)
        assert article.name == u'Some article'
        assert article.content == u'Some content'

    def test_delete(self):
        article = self.Article()
        article.description = u'Some description'
        self.session.add(article)
        self.session.commit()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.delete(article)
        self.session.commit()

    def test_current_translation_as_object_property(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        with article.force_locale('fi'):
            assert article.current_translation == article._translation_fi

            assert article.current_translation == article._translation_fi
            article._translation_fi


class TestCurrentTranslation(TestCase):
    def create_models(self):
        class Locale(object):
            def __init__(self, value):
                self.value = value

            def __unicode__(self):
                return self.value

        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255), nullable=False),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': ['en', 'fi'],
                'default_locale': 'en'
            }

            def get_locale(self):
                return Locale('en')

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)

        self.Article = Article

    def test_converts_locale_object_to_unicode(self):
        article = self.Article()
        article.name = u'Some article'
        assert article.name == u'Some article'

    def test_current_translation_as_class_property(self):
        assert self.Article.current_translation
