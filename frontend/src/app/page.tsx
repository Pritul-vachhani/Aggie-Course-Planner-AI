import PreferenceForm from '../components/PreferenceForm';
import CourseCard from '../components/CourseCard';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-extrabold text-black mb-2">AggieAI</h1>
        </header>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <PreferenceForm />
          </div>
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-2xl font-bold text-black mb-4">Recommendations</h2>
            <CourseCard />
            <CourseCard />
          </div>
        </div>
      </div>
    </main>
  );
}