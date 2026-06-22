import InputPage from './pages/InputPage'

/**
 * App.jsx
 * Root component. Week 1: just renders InputPage.
 * Week 5: add React Router here for Dashboard + Report pages.
 *
 *   <Route path="/"          element={<InputPage />} />
 *   <Route path="/results"   element={<Dashboard />} />
 */
export default function App() {
  return <InputPage />
}
