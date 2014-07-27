from pyeve.www.core import Page, UIModuleDescriptior
from pyeve.www.html import HtmlLayout

__author__ = 'Rudy'


SkillsModule = UIModuleDescriptior('Skills', 'skills')
SkillsModule.addPage('overview', lambda: SkillsOverview, 'Overview')
SkillsModule.addPage('queue', lambda: SkillsQueue, 'Train queue')
SkillsModule.addPage('plans', lambda: SkillsPlans, 'Manage plans')


class SkillsOverview(Page):
    def doGet(self, request):
        layout = HtmlLayout()
        layout.setContent('Skills list, etc')

        return layout


class SkillsQueue(Page):
    def doGet(self, request):
        layout = HtmlLayout()
        layout.setContent('Skills queue')

        return layout


class SkillsPlans(Page):
    def doGet(self, request):
        layout = HtmlLayout()
        layout.setContent('Skills plans')

        return layout