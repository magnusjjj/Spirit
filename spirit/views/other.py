# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

from spirit.utils.ratelimit.decorators import ratelimit
from spirit.utils.decorators import moderator_required
from spirit.models.category import Category
from spirit.models.comment import MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED
from spirit.forms.comment import CommentForm
from spirit.forms.topic_other import TopicOtherForm
from spirit.signals.comment import comment_posted
from spirit.forms.topic_poll import TopicPollForm, TopicPollChoiceFormSet

from spirit.models.topic import Topic
from spirit.forms.topic import TopicForm
#from spirit.signals.topic import topic_viewed, topic_post_moderate


@login_required
@ratelimit(rate='1/10s')
def other_publish(request, other_type_id, other_object_id):
    if request.method == 'POST':
        form = TopicOtherForm(user=request.user, data=request.POST,other_category_id=other_object_id, other_category_content_type=other_type_id)
        cform = CommentForm(user=request.user, data=request.POST)
        pform = TopicPollForm(data=request.POST)
        pformset = TopicPollChoiceFormSet(can_delete=False, data=request.POST)

        if not request.is_limited and form.is_valid() and cform.is_valid() \
                and pform.is_valid() and pformset.is_valid():
            # wrap in transaction.atomic?
            topic = form.save()

            cform.topic = topic
            comment = cform.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=cform.mentions)

            # Create a poll only if we have choices
            if pformset.is_filled():
                pform.topic = topic
                poll = pform.save()
                pformset.instance = poll
                pformset.save()

            return redirect(topic.get_absolute_url())
    else:
        form = TopicOtherForm(user=request.user, other_category_id=other_object_id, other_category_content_type=other_type_id, initial={'category': 0})
        cform = CommentForm()
        pform = TopicPollForm()
        pformset = TopicPollChoiceFormSet(can_delete=False)

    return render(request, 'spirit/topic/topic_publish.html', {'form': form, 'cform': cform,
                                                               'pform': pform, 'pformset': pformset})
