import DIDConnect from './components/DIDConnect'
import SignalUpload from './components/SignalUpload'
import EventLog from './components/EventLog'
import InfluenceDashboard from './components/InfluenceDashboard'
import ObserverReview from './components/ObserverReview'
import ScarRecovery from './components/ScarRecovery'

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-6xl">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-3 text-gray-900">
          Deed Ledger
        </h1>
        <p className="text-lg text-gray-600">
          Portable deed-based reputation. Verify actions, earn trust.
        </p>
      </header>

      <div className="grid gap-8 md:grid-cols-2">
        {/* DID Connection */}
        <section className="card">
          <h2 className="text-2xl font-semibold mb-4">Connect</h2>
          <DIDConnect />
        </section>

        {/* Signal Upload */}
        <section className="card">
          <h2 className="text-2xl font-semibold mb-4">Submit Signal</h2>
          <SignalUpload />
        </section>

        {/* Influence Dashboard */}
        <section className="card md:col-span-2">
          <h2 className="text-2xl font-semibold mb-4">Influence Dashboard</h2>
          <InfluenceDashboard />
        </section>

        {/* Event Log */}
        <section className="card md:col-span-2">
          <h2 className="text-2xl font-semibold mb-4">Event Log</h2>
          <EventLog />
        </section>

        {/* Scar Recovery */}
        <section id="scar-recovery" className="card md:col-span-2">
          <ScarRecovery />
        </section>

        {/* Observer Review */}
        <section className="card md:col-span-2">
          <h2 className="text-2xl font-semibold mb-4">Observer Review</h2>
          <ObserverReview />
        </section>
      </div>

      <footer className="mt-16 text-center text-sm text-gray-500">
        <p>Trust is earned through work, not wealth.</p>
        <p className="mt-1">Reputation fades without contribution.</p>
      </footer>
    </main>
  )
}
