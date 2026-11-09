# Crystal POS Frontend

Vue 3 + TypeScript + Vite frontend. In production it is built into `dist/` and served by the Django backend at http://localhost:8010. The API base URL is http://localhost:8010/api.

## Project Setup

```sh
npm install
```

### Development server

Start the backend first (`cd backend && python manage.py runserver 8010`), then:

```sh
npm run dev -- --host 127.0.0.1
```

Access at http://localhost:5173.

### Build

```sh
npm run build
```

### Type-check

```sh
npm run type-check
```

### Unit tests (Vitest)

```sh
npm run test:unit
```
