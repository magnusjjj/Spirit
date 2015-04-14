# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType, ContentTypeManager

from . import register
from spirit.models.topic import Topic
from spirit.models.category import Category

@register.inclusion_tag('spirit/topic_other/topic_list.html', takes_context=True)
def forum_other(context, object):
	content_t = ContentType.objects.get_for_model(object)
	context["objectid"] = object.pk
	context["typeid"] = content_t.pk
	
	topics = Topic.objects\
			.visible()\
			.with_bookmarks(user=context["user"])\
			.filter(other_category_content_type=content_t, other_category_id=object.pk)\
			.select_related('category')
	
	categories = Category.objects\
        .visible()\
        .parents()

	context["categories"] = categories
	context["topics"] = topics
	return context
