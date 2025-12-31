export default function PhaseOverview() {
  const phases = [
    {
      number: 2,
      name: "Architecture Sommelier",
      description: "AI analyzes your requirements and suggests optimal GCP services",
      icon: "🎨",
      status: "pending"
    },
    {
      number: 3,
      name: "Machine Specification",
      description: "Determines precise compute, memory, and storage specifications",
      icon: "⚙️",
      status: "pending"
    },
    {
      number: 4,
      name: "Pricing Calculation",
      description: "Real-time cost estimation with GCP pricing API",
      icon: "💵",
      status: "pending"
    },
    {
      number: 5,
      name: "Trade-off Analysis",
      description: "Explore alternative configurations and cost-performance trade-offs",
      icon: "⚖️",
      status: "pending"
    },
    {
      number: 6,
      name: "Recommendation",
      description: "Final optimized architecture with detailed specifications and costs",
      icon: "✨",
      status: "pending"
    }
  ];

  return (
    <section className="py-16 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-900 mb-3 text-center">
          How It Works
        </h2>
        <p className="text-gray-600 mb-12 text-center max-w-2xl mx-auto">
          Our 8-phase AI pipeline analyzes your requirements and generates production-ready infrastructure recommendations
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {phases.map((phase) => (
            <div
              key={phase.number}
              className="bg-gradient-to-br from-slate-50 to-gray-50 border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-start gap-4">
                <div className="text-4xl">{phase.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      Phase {phase.number}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {phase.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {phase.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-8">
          <div className="flex items-start gap-4">
            <div className="text-4xl">🚀</div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Ready to Deploy
              </h3>
              <p className="text-gray-700">
                Get production-ready Terraform configurations, Docker files, and CI/CD pipelines. 
                Deploy your optimized infrastructure to GCP in minutes, not weeks.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
