export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 py-20 px-4">
      <div className="max-w-6xl mx-auto text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          InfronAI
        </h1>
        <p className="text-xl md:text-2xl text-blue-100 mb-4 max-w-3xl mx-auto">
          AI-Powered GCP Architecture Recommendations
        </p>
        <p className="text-base md:text-lg text-blue-200 max-w-2xl mx-auto">
          Describe your application in plain English. Get intelligent, cost-optimized infrastructure recommendations in seconds.
        </p>
        
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 text-white">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="font-semibold mb-2">Intent-Driven</h3>
            <p className="text-sm text-blue-100">Natural language understanding of your requirements</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 text-white">
            <div className="text-3xl mb-2">🏗️</div>
            <h3 className="font-semibold mb-2">Smart Architecture</h3>
            <p className="text-sm text-blue-100">AI-powered service selection and configuration</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 text-white">
            <div className="text-3xl mb-2">💰</div>
            <h3 className="font-semibold mb-2">Cost Optimized</h3>
            <p className="text-sm text-blue-100">Real-time pricing analysis and trade-offs</p>
          </div>
        </div>
      </div>
    </section>
  );
}
