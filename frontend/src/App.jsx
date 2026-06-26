import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/shared/Sidebar'
import DashboardPage from './pages/DashboardPage'
import PredictionsPage from './pages/PredictionsPage'
import RecommendationsPage from './pages/RecommendationsPage'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />

        <main style={{
          marginLeft: 220,
          flex: 1,
          padding: '32px 36px',
          maxWidth: 1400,
          width: '100%',
        }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
