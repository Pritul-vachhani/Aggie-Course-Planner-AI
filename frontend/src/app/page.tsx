'use client';

import { useState } from 'react';

type CourseCardProps = {
  title: string;
  rank: number;
  explanation: string;
  units: string | number;
};

// Polished, ranked Course Card with hover effects and Aggie colors
function CourseCard({ title, rank, explanation, units }: CourseCardProps) {
  return (
    <article className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 p-6 flex gap-5 relative overflow-hidden group">
      {/* Decorative left border on hover */}
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#B3A369] transform origin-left scale-y-0 group-hover:scale-y-100 transition-transform duration-300"></div>
      
      <div className="shrink-0">
        <div className="w-12 h-12 rounded-full bg-[#022851] text-[#B3A369] font-black flex items-center justify-center text-xl shadow-md">
          #{rank}
        </div>
      </div>
      
      <div className="flex-1">
        <div className="flex justify-between items-start gap-4 mb-2">
          <h4 className="text-lg font-bold text-gray-900">{title}</h4>
          <span className="shrink-0 text-xs font-bold tracking-wider text-gray-500 uppercase bg-gray-50 border border-gray-200 px-3 py-1 rounded-md">
            {units} Units
          </span>
        </div>
        <p className="text-gray-600 leading-relaxed text-sm">{explanation}</p>
      </div>
    </article>
  );
}

export default function Home() {
  // Form State
  const [interests, setInterests] = useState('');
  const [ge, setGe] = useState('Any');
  const [units, setUnits] = useState('Any');
  const [major, setMajor] = useState('Any');
  const [completed, setCompleted] = useState('');

  // Results State
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!interests.trim()) return;

    setIsLoading(true);
    setHasSearched(true);
    setError('');
    setRecommendations([]);

    try {
      const payload: Record<string, any> = {
        interests: [interests]
      };

      // Keys must match StudentProfile in backend/app/schemas/recommend.py
      if (ge !== 'Any') payload.remaining_ge = [ge];
      if (units !== 'Any') payload.preferred_units = parseInt(units, 10);
      if (major !== 'Any') payload.major = major;
      if (completed.trim() !== '') {
        payload.completed_courses = completed.split(',').map((c) => c.trim()).filter(Boolean);
      }

      const response = await fetch('http://localhost:8000/recommend/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Backend Error: ${response.status}`);
      }

      const data = await response.json();
      // Backend returns { recommendations: [{ course, match_score, reasons }] }
      setRecommendations((data.recommendations ?? []).slice(0, 5)); // Enforce top 5 limit as per project specs
    } catch (err) {
      console.error(err);
      setError('AggieAI is currently offline or encountered an error. Please ensure the FastAPI backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f8f9fa] font-sans selection:bg-[#B3A369] selection:text-[#022851]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-black tracking-tight text-[#022851]">
            Aggie<span className="text-[#B3A369]">AI</span>
          </h1>
          <span className="text-sm font-semibold text-gray-400 bg-gray-100 px-3 py-1 rounded-full">MVP v1.0</span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10 grid lg:grid-cols-12 gap-10">
        
        {/* Left Column: Configuration Panel */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-1">Design Your Quarter</h2>
            <p className="text-sm text-gray-500 mb-8">Set your parameters and let the AI find your perfect schedule.</p>

            <form onSubmit={handleSearch} className="space-y-5">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Academic Interests *</label>
                <textarea 
                  required
                  rows={3}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 focus:border-[#B3A369] outline-none transition-all resize-none"
                  placeholder="e.g., I want a chill class about film, cognitive psychology, or modern technology..."
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">Target GE</label>
                  <select 
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-sm focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                    value={ge}
                    onChange={(e) => setGe(e.target.value)}
                  >
                    <option value="Any">Any GE</option>
                    <option value="Arts & Humanities (AH)">Arts & Humanities (AH)</option>
                    <option value="Science & Engineering (SE)">Science & Engineering (SE)</option>
                    <option value="Social Sciences (SS)">Social Sciences (SS)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">Units</label>
                  <select 
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-sm focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                    value={units}
                    onChange={(e) => setUnits(e.target.value)}
                  >
                    <option value="Any">Any</option>
                    <option value="3">3 Units</option>
                    <option value="4">4 Units</option>
                    <option value="5">5 Units</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Major Constraints</label>
                <select 
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-sm focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                  value={major}
                  onChange={(e) => setMajor(e.target.value)}
                >
                  <option value="Any">Any Subject</option>
                  <option value="Cognitive Science">Cognitive Science</option>
                  <option value="Data Science">Data Science</option>
                  <option value="Computer Science">Computer Science</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Completed Prerequisites <span className="font-normal text-gray-400">(Optional)</span></label>
                <input 
                  type="text"
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-sm focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none"
                  placeholder="e.g., ECS 032A, MAT 021A"
                  value={completed}
                  onChange={(e) => setCompleted(e.target.value)}
                />
              </div>

              <button 
                type="submit"
                disabled={isLoading}
                className="w-full bg-[#022851] hover:bg-[#022851]/90 text-white font-bold text-sm py-4 rounded-xl shadow-md transition-all active:scale-[0.98] disabled:opacity-70 mt-4"
              >
                {isLoading ? 'Analyzing Catalog...' : 'Generate Recommendations'}
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: AI Output */}
        <div className="lg:col-span-8 relative">
          
          {/* State 1: Empty / Landing (Only shows before first search) */}
          {!hasSearched && (
            <div className="h-full min-h-[500px] flex flex-col items-center justify-center text-center px-10 border-2 border-dashed border-gray-200 rounded-3xl bg-gray-50/50">
              <div className="w-20 h-20 bg-white shadow-sm rounded-2xl flex items-center justify-center mb-6">
                 <span className="text-4xl">📚</span>
              </div>
              <h3 className="text-2xl font-bold text-[#022851] mb-2">Ready to explore?</h3>
              <p className="text-gray-500 max-w-sm">
                Describe your ideal class on the left. AggieAI will scan the catalog using semantic search to find your perfect matches.
              </p>
            </div>
          )}

          {/* State 2: Loading */}
          {isLoading && (
            <div className="space-y-4">
              {[1, 2, 3].map((skeleton) => (
                <div key={skeleton} className="bg-white rounded-2xl border border-gray-100 p-6 h-32 animate-pulse flex gap-5">
                   <div className="w-12 h-12 bg-gray-200 rounded-full shrink-0"></div>
                   <div className="flex-1 space-y-3 pt-2">
                     <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                     <div className="h-3 bg-gray-100 rounded w-full"></div>
                     <div className="h-3 bg-gray-100 rounded w-5/6"></div>
                   </div>
                </div>
              ))}
            </div>
          )}

          {/* State 3: Error */}
          {error && !isLoading && (
            <div className="bg-red-50 text-red-800 p-6 rounded-2xl border border-red-100 flex items-start gap-4">
               <span className="text-2xl">⚠️</span>
               <div>
                 <h4 className="font-bold mb-1">Connection Failed</h4>
                 <p className="text-sm">{error}</p>
               </div>
            </div>
          )}

          {/* State 4: Results Rendering */}
          {!isLoading && !error && hasSearched && recommendations.length > 0 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Top 5 Matches</h3>
                <span className="text-sm font-semibold text-[#B3A369]">Powered by all-MiniLM-L6-v2</span>
              </div>
              
              {recommendations.map((rec, index) => (
                <CourseCard
                  key={rec.course?.course_code ?? index}
                  rank={index + 1}
                  title={rec.course ? `${rec.course.course_code}: ${rec.course.title}` : "Course Title"}
                  explanation={rec.reasons?.join(' ') || rec.course?.description || "Matches your academic interests and constraints."}
                  units={rec.course?.units ?? units}
                />
              ))}
            </div>
          )}

          {/* State 5: No Results Found */}
          {!isLoading && !error && hasSearched && recommendations.length === 0 && (
            <div className="text-center py-20 bg-white rounded-3xl border border-gray-100">
              <span className="text-4xl mb-4 block">🔍</span>
              <h3 className="text-lg font-bold text-gray-900">No perfect matches found.</h3>
              <p className="text-gray-500 mt-2">Try adjusting your filters or broadening your interests.</p>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}