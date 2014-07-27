import pkg_resources

__author__ = 'Rudy'


def initRouting(app):
    """

    :type app: pyeve.www.core.PyEveWsgiApp
    """
    from pyeve.www.pages.login import LoginPage, LogoutPage, RegisterAccount
    from pyeve.www.pages.profile import ProfilePage
    # from pyeve.www.pages.skills import SkillsOverview

    app.registerPage('/', 'index', LoginPage)
    app.registerPage('/register', 'register', RegisterAccount)
    app.registerPage('/logout', 'logout', LogoutPage)
    # app.registerPage('/profile', 'profile', ProfilePage)
    # app.registerPage('/skills', 'skills', SkillsOverview)
    #
    # app.registerPage('/fittings', 'fittings', None)
    # app.registerPage('/assets', 'assets', None)

    for ep in pkg_resources.iter_entry_points('UIModules'):
        #: :type: pyeve.www.core.UIModuleDescriptior
        mod = ep.load()

        for pageInfo in mod.pages:
            app.registerPage(pageInfo.url, pageInfo.endpoint, pageInfo.clazzFactory())