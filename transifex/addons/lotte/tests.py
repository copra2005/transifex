from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.utils import simplejson as json
from txcommon.tests.base import BaseTestCase


Translation = get_model('resources', 'Translation')


def default_params():
    """Return the default parameters (in a dict) for the DataTables interaction."""
    return { 'bEscapeRegex':True, 'bEscapeRegex_0':True, 
        'bEscapeRegex_1':True, 'bEscapeRegex_2':True, 'bEscapeRegex_3':True,
        'bEscapeRegex_4':True, 'bEscapeRegex_5':True, 'bSearchable_0':True,
        'bSearchable_1':True, 'bSearchable_2':True, 'bSearchable_3':True,
        'bSearchable_4':True, 'bSearchable_5':True, 'bSortable_0':True,
        'bSortable_1':False, 'bSortable_2':True, 'bSortable_3':False,
        'bSortable_4':False, 'bSortable_5':False, 'iColumns':6, 
        'iDisplayLength':10, 'iDisplayStart':0, 'iSortCol_0':0, 'iSortingCols':1,
        'sSortDir_0':'asc'}

class LotteViewsTests(BaseTestCase):

    def setUp(self):
        super(LotteViewsTests, self).setUp()
        self.entity = self.resource.entities[0]

        self.DataTable_params = default_params()

        # Set some custom translation data
        # Source strings
        self.source_string_plural1 = self.source_entity_plural.translations.create(
            string="SourceArabicTrans1",
            language=self.language_en,
            user=self.user["maintainer"], rule=1)
        self.source_string_plural2 = self.source_entity_plural.translations.create(
            string="SourceArabicTrans2",
            language=self.language_en,
            user=self.user["maintainer"], rule=5)
        # Translation strings
        self.source_entity_plural.translations.create(
            string="ArabicTrans0", language=self.language_ar,
            user=self.user["maintainer"], rule=0)
        self.source_entity_plural.translations.create(
            string="ArabicTrans1", language=self.language_ar,
            user=self.user["maintainer"], rule=1)
        self.source_entity_plural.translations.create(
            string="ArabicTrans2", language=self.language_ar,
            user=self.user["maintainer"], rule=2)
        self.source_entity_plural.translations.create(
            string="ArabicTrans3", language=self.language_ar,
            user=self.user["maintainer"], rule=3)
        self.source_entity_plural.translations.create(
            string="ArabicTrans4", language=self.language_ar,
            user=self.user["maintainer"], rule=4)
        self.source_entity_plural.translations.create(
            string="ArabicTrans5", language=self.language_ar,
            user=self.user["maintainer"], rule=5)

        # URLs
        self.snippet_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        self.translate_view_url = reverse('translate_resource',
            args=[self.project.slug, self.resource.slug, self.language.code])
        self.translate_content_arabic_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language_ar.code])
        self.push_translation = reverse('push_translation',
            args=[self.project.slug, self.language_ar.code])

    def tearDown(self):
        super(LotteViewsTests, self).tearDown()
        self.source_entity_plural.translations.all().delete()

    def test_snippet_entities_data(self):
        """Test the entity details part of the snippet is correct."""
        # Create custom fields in entity
        self.entity.string = "Key1"
        self.entity.context = "Description1"
        self.entity.occurrences = "Occurrences1"
        self.entity.save()
        # Test the response contents
        resp = self.client['team_member'].get(self.snippet_url)
        self.assertContains(resp, self.entity.string, status_code=200)
        self.assertContains(resp, self.entity.context)
        self.assertContains(resp, self.entity.occurrences)
        self.assertTemplateUsed(resp, 'lotte_details_snippet.html')

    def test_snippet_translation_data(self):
        """Test the translation details part of the snippet is correct."""
        # Set some custom data
        self.entity.translations.create(string="StringTrans1",
            language=self.language, user=self.user["team_member"])
        # Test the response contents
        resp = self.client['team_member'].get(self.snippet_url)
        self.assertContains(resp, '0 minutes', status_code=200)

    def test_translate_view(self):
        """Test the basic response of the main view for lotte."""
        # Check page status
        resp = self.client['maintainer'].get(self.translate_view_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'translate.html')

    def test_plural_data(self):
        """Test that all plural fields are sent."""

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_en).count(), 2)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 6)

        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertContains(resp, 'ArabicTrans1', status_code=200)
        self.assertContains(resp, 'ArabicTrans2')
        self.assertContains(resp, 'ArabicTrans3')
        self.assertContains(resp, 'ArabicTrans4')

    def test_push_plural_translation(self):
        """Test pushing pluralized translations."""
        data1 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"ArabicTrans0",
                                "one":"ArabicTrans1",
                                "few":"ArabicTrans3",
                                "other":"ArabicTrans5",}
                           },]
               }
        data2 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"ArabicTrans0",
                                "one":"ArabicTrans1",
                                "two":"ArabicTrans2",
                                "few":"ArabicTrans3",
                                "many":"ArabicTrans4",}
                           },]
               }
        data3 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"ArabicTrans0",
                                "one":"ArabicTrans1",
                                "two":"ArabicTrans2",
                                "few":"ArabicTrans3",
                                "many":"ArabicTrans4",
                                "other":"ArabicTrans5",}
                           },]
               }
        data4 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"",
                                "one":"",
                                "two":"",
                                "few":"",
                                "many":"",
                                "other":"",}
                           },]
               }
        resp1 = self.client['maintainer'].post(self.push_translation,
            json.dumps(data1), content_type='application/json')
        self.assertContains(resp1,
            'All the plural translations must be filled in', status_code=200)

        resp2 = self.client['maintainer'].post(self.push_translation,
            json.dumps(data2), content_type='application/json')
        self.assertContains(resp2,
            'All the plural translations must be filled in', status_code=200)

        resp3 = self.client['maintainer'].post(self.push_translation,
            json.dumps(data3), content_type='application/json')
        self.assertContains(resp3, 'Translation updated successfully',
            status_code=200)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 6)

        resp4 = self.client['maintainer'].post(self.push_translation,
            json.dumps(data4), content_type='application/json')
        self.assertContains(resp4, 'Translation updated successfully',
            status_code=200)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 0)

        # We push again the data to return to the setup state.
        resp5 = self.client['maintainer'].post(self.push_translation,
            json.dumps(data3), content_type='application/json')
        self.assertContains(resp3, 'Translation updated successfully',
            status_code=200)
        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 6)

    def test_dt_search_string(self):
        """Test the Datatable's search."""
        self.DataTable_params["sSearch"] = "ArabicTrans"
        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertContains(resp, 'ArabicTrans', status_code=200)
        self.DataTable_params["sSearch"] = "Empty result"
        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertNotContains(resp, 'ArabicTrans', status_code=200)

    def test_dt_pagination(self):
        """Test the Datatable's pagination mechanism."""
        self.DataTable_params["iDisplayStart"] = 0
        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertContains(resp, 'ArabicTrans', status_code=200)

    def test_dt_show_num_entries(self):
        """Test the Datatable's show num entries mechanism."""
        self.DataTable_params["iDisplayLength"] = 20
        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertContains(resp, 'ArabicTrans', status_code=200)

    def test_filters(self):
        """Test lotte filters one by one."""
        pass


class LotteTemplateTests(BaseTestCase):

    def setUp(self):
        super(LotteTemplateTests, self).setUp()
        # URLs
        self.translate_view_url = reverse('translate_resource',
            args=[self.project.slug, self.resource.slug, self.language.code])
        self.translate_content_arabic_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language_ar.code])

    def tearDown(self):
        super(LotteTemplateTests, self).tearDown()

    def test_search_translation_link(self):
        """Test that search translation link exists and points to search page."""

        # Test the response contents
        resp = self.client['team_member'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')
        self.assertContains(resp, 'Search translations', status_code=200)
        self.assertContains(resp,
            'Search in Transifex memory for existing translations (opens up in new tab/window)')
        self.assertContains(resp, reverse('search_translations'))

    def test_filters(self):
        """Test that more languages, filter by users, resources appear."""

        # Test the response contents
        resp = self.client['team_member'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')
        self.assertContains(resp, 'More languages', status_code=200)
        self.assertContains(resp,
            'Show translations of<br /> the chosen languages')
        self.assertContains(resp, '<input class="more_languages" type="checkbox"')
        self.assertContains(resp, 'Filter by users')
        self.assertContains(resp,
            'Show only the translations<br />of the chosen users')
        self.assertContains(resp, 'No active contributor!')

    def test_statistics_div(self):
        """Test that statistics div appears correctly."""

        # Test the response contents
        resp = self.client['team_member'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')

        self.assertContains(resp, 'Translated', status_code=200)
        self.assertContains(resp, 'Untranslated')
        self.assertContains(resp, 'Modified')
        self.assertContains(resp, 'Total')
        self.assertContains(resp, ('<input id="translated" class="filters" '
            'type="checkbox"  checked="checked"  name="only_translated"/>'))
        self.assertContains(resp, ('<input id="untranslated" class="filters" '
            'type="checkbox" checked="checked" name="only_untranslated"/>'))

    def test_footpanel_div(self):
        """Check that footpanel html snippet appears correctly."""
        # Test the response contents
        resp = self.client['team_member'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')

        self.assertContains(resp, 'General Settings', status_code=200)
        self.assertContains(resp, 'Verbose editing')
        self.assertContains(resp, 'Auto save')

    def test_global_buttons(self):
        """Check that "Save all", "Delete translations", "Save and Exit" appear."""
        # Test the response contents
        resp = self.client['team_member'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')

        self.assertContains(resp, 'Save all', status_code=200)
        self.assertContains(resp, 'Save and Exit')
        # For the team_member "delete" should not appear
        self.assertNotContains(resp, 'Delete translations')

        # Test the response contents
        resp = self.client['maintainer'].get(self.translate_view_url)
        self.assertTemplateUsed(resp, 'translate.html')
        # For the team_member "delete" should not appear
        self.assertContains(resp, 'Delete translations')


class LottePermissionsTests(BaseTestCase):

    def setUp(self):
        super(LottePermissionsTests, self).setUp()
        self.entity = self.resource.entities[0]
        self.DataTable_params = default_params()

    def tearDown(self):
        super(LottePermissionsTests, self).tearDown()

    def test_anon(self):
        """
        Test anonymous user
        """
        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % page_url)

        # Test view_strings
        page_url = reverse('view_strings', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test exit
        page_url = reverse('exit_lotte', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % page_url)
        # POST
        resp = self.client['anonymous'].post(page_url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % page_url)

        # Test delete translation
        page_url = reverse('delete_translation', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 403)
        # POST
        resp = self.client['anonymous'].post(page_url)
        self.assertEqual(resp.status_code, 403)

        # Test stringset handling Ajax call
        page_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language.code])
        # POST
        resp = self.client['anonymous'].post(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)
        # GET
        resp = self.client['anonymous'].get(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['anonymous'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 302)
        source_trans.delete()

        # Test translation details
        page_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        # Test the response contents
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 200)

    def test_registered(self):
        """
        Test random registered user
        """
        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['registered'].get(page_url)
        self.assertEqual(resp.status_code, 403)

        # Test view_strings
        page_url = reverse('view_strings', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['registered'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test exit
        page_url = reverse('exit_lotte', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['registered'].get(page_url, follow=True)
        self.assertEqual(resp.status_code, 403)
        # POST
        resp = self.client['registered'].post(page_url, follow=True)
        self.assertEqual(resp.status_code, 403)

        # Test delete translation
        page_url = reverse('delete_translation', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['registered'].get(page_url)
        self.assertEqual(resp.status_code, 403)
        # POST
        resp = self.client['team_member'].post(page_url)
        self.assertEqual(resp.status_code, 403)

        # Test stringset handling Ajax call
        page_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language.code])
        # POST
        resp = self.client['registered'].post(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)
        # GET
        resp = self.client['registered'].get(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['registered'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 403)
        source_trans.delete()

        # Test translation details
        page_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        # Test the response contents
        resp = self.client['registered'].get(page_url)
        self.assertEqual(resp.status_code, 200)

    def test_team_member(self):
        """
        Test team_member permissions
        """
        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test view_strings
        page_url = reverse('view_strings', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test exit
        page_url = reverse('exit_lotte', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['team_member'].get(page_url, follow=True)
        self.assertEqual(resp.status_code, 200)
        # POST
        resp = self.client['team_member'].post(page_url, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Test delete translation
        page_url = reverse('delete_translation', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 403)
        # POST
        resp = self.client['team_member'].post(page_url)
        self.assertEqual(resp.status_code, 403)

        # Test stringset handling Ajax call
        page_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language.code])
        # POST
        resp = self.client['team_member'].post(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)
        # GET
        resp = self.client['team_member'].get(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)

        # Test main lotte page for other team. This should fail
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, 'el'])
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 403)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['team_member'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 200)

        # Create new translation in other team. Expect this to fail
        resp = self.client['team_member'].post(reverse('push_translation',
            args=[self.project.slug, 'ru']),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 403)
        source_trans.delete()

        # Test translation details
        page_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        # Test the response contents
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 200)

    def test_maintainer(self):
        """
        Test maintainer permissions
        """
        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['maintainer'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test view_strings
        page_url = reverse('view_strings', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['maintainer'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test exit
        page_url = reverse('exit_lotte', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['maintainer'].get(page_url, follow=True)
        self.assertEqual(resp.status_code, 200)
        # POST
        resp = self.client['maintainer'].post(page_url, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Test delete translation
        page_url = reverse('delete_translation', args=[
            self.project.slug, self.language.code])
        # GET
        resp = self.client['maintainer'].get(page_url)
        self.assertEqual(resp.status_code, 400)
        # POST
        resp = self.client['maintainer'].post(page_url, json.dumps(
            {"to_delete":[self.entity.id]}),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # Test stringset handling Ajax call
        page_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language.code])
        # POST
        resp = self.client['maintainer'].post(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)
        # GET
        resp = self.client['maintainer'].get(page_url, self.DataTable_params)
        self.assertEqual(resp.status_code, 200)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['maintainer'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 200)
        source_trans.delete()

        # Test translation details
        page_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        # Test the response contents
        resp = self.client['maintainer'].get(page_url)
        self.assertEqual(resp.status_code, 200)
