import WebApp from '@twa-dev/sdk';

export const UserProfile = () => {
  const user = WebApp.initDataUnsafe.user;

  if (!user) {
    return <div>Пользователь не авторизован</div>;
  }

  return (
    <div className="user-profile">
      <h2>Профиль пользователя</h2>
      <div className="user-info">
        <p><strong>ID:</strong> {user.id}</p>
        <p><strong>Имя:</strong> {user.first_name}</p>
        {user.last_name && <p><strong>Фамилия:</strong> {user.last_name}</p>}
        {user.username && <p><strong>Username:</strong> @{user.username}</p>}
        {user.language_code && <p><strong>Язык:</strong> {user.language_code}</p>}
      </div>
    </div>
  );
}; 