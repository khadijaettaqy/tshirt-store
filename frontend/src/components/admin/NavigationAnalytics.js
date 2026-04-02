import React from 'react';

export default function NavigationAnalytics({ data }) {
  const { most_visited, device_breakdown, session_analytics } = data || {};
  return (
    <div className="space-y-6">
      {most_visited && (
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Most Visited Pages</h3>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Page</th><th className="text-right py-2">Visits</th><th className="text-right py-2">Avg Duration</th></tr></thead>
            <tbody>
              {most_visited.map((p, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="py-2 font-mono text-indigo-600">{p.path}</td>
                  <td className="text-right">{p.count}</td>
                  <td className="text-right">{p.avg_duration?.toFixed(0) || 0}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {device_breakdown && (
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Device Breakdown</h3>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(device_breakdown).map(([type, count]) => (
              <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
                <i className={`fas ${type === 'mobile' ? 'fa-mobile-alt' : type === 'tablet' ? 'fa-tablet-alt' : 'fa-desktop'} text-3xl text-indigo-500 mb-2`}></i>
                <p className="capitalize font-semibold">{type}</p>
                <p className="text-2xl font-bold text-indigo-600">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {session_analytics && (
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Session Analytics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Sessions', value: session_analytics.total_sessions },
              { label: 'Avg Pages/Session', value: session_analytics.avg_pages_per_session?.toFixed(1) },
              { label: 'Avg Duration', value: `${session_analytics.avg_session_duration?.toFixed(0)}s` },
              { label: 'Bounce Rate', value: `${((session_analytics.bounce_rate || 0) * 100).toFixed(1)}%` },
            ].map(s => (
              <div key={s.label} className="text-center p-4 bg-indigo-50 rounded-lg">
                <p className="text-sm text-gray-600">{s.label}</p>
                <p className="text-2xl font-bold text-indigo-600">{s.value || 0}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
