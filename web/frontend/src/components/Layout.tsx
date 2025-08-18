import { Outlet, Link, useLocation } from 'react-router-dom';
import { Brain, Users, TrendingUp, Target, Settings } from 'lucide-react';

const Layout = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Дашборд', href: '/', icon: Brain },
    { name: 'Популяция', href: '/population', icon: Users },
    { name: 'Эволюция', href: '/evolution', icon: TrendingUp },
    { name: 'Задачи', href: '/tasks', icon: Target },
    { name: 'Настройки', href: '/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-brain-500 to-brain-600 flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Brainzzz</span>
          </div>
        </div>

        <nav className="mt-8 px-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                      isActive
                        ? 'bg-brain-50 text-brain-700 border-r-2 border-brain-500'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <item.icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="absolute bottom-4 left-4 right-4">
          <div className="rounded-lg bg-gray-50 p-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-full bg-brain-500"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Инкубатор</p>
                <p className="text-xs text-gray-500">Активен</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
