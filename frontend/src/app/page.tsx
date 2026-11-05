'use client';

import { useState } from 'react';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');
const API_URL = API_BASE_URL.replace(/\/+$/, '');

type CourseCardProps = {
  title: string;
  rank: number;
  description: string;
  details: string;
  units: string | number;
  prerequisites: string;
};

type Recommendation = {
  course: {
    course_code: string;
    title: string;
    description: string;
    details: string;
    units: string;
    prerequisites: string;
    ge_categories: string[];
  };
  match_score: number;
  reasons: string[];
};

type RecommendationRequest = {
  interests: string;
  top_k: number;
  course_level: CourseLevel;
  remaining_ge?: string[];
  preferred_units?: number;
  subject?: string;
  completed_courses?: string[];
};

type CourseLevel = 'undergraduate' | 'lower' | 'upper' | 'graduate';

// Polished, ranked Course Card with hover effects and Aggie colors
function CourseCard({ title, rank, description, details, units, prerequisites }: CourseCardProps) {
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
        {description.trim() && (
          <p className="text-sm leading-relaxed text-gray-600">{description}</p>
        )}
        <div className="mt-4">
          <h5 className="text-sm font-bold text-gray-800">Course details</h5>
          <p className="mt-1 whitespace-pre-line text-sm text-gray-600">
            {details.trim() || 'None listed'}
          </p>
        </div>
        <div className="mt-4 border-t border-gray-100 pt-3">
          <h5 className="text-sm font-bold text-gray-800">Prerequisites</h5>
          <p className="mt-1 text-sm text-gray-600">
            {prerequisites.trim() || 'None listed'}
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Verify prerequisites and enrollment eligibility with UC Davis before registering.
          </p>
        </div>
      </div>
    </article>
  );
}

export default function Home() {
  // Form State
  const [interests, setInterests] = useState('');
  const [ge, setGe] = useState('Any');
  const [units, setUnits] = useState('Any');
  const [studentLevel, setStudentLevel] = useState<CourseLevel | ''>('');
  const [coursePrefix, setCoursePrefix] = useState('');
  const [completed, setCompleted] = useState('');

  // Results State
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!interests.trim() || !studentLevel) return;

    setIsLoading(true);
    setHasSearched(true);
    setError('');
    setRecommendations([]);

    try {
      const payload: RecommendationRequest = {
        interests: interests.trim(),
        top_k: 5,
        course_level: studentLevel,
      };

      // Keys must match StudentProfile in backend/app/schemas/recommend.py
      if (ge !== 'Any') payload.remaining_ge = [ge];
      if (units !== 'Any') payload.preferred_units = Number(units);
      if (coursePrefix.trim()) payload.subject = coursePrefix.trim().toUpperCase();
      if (completed.trim() !== '') {
        payload.completed_courses = completed.split(',').map((c) => c.trim()).filter(Boolean);
      }

      const controller = new AbortController();
      const requestTimeout = setTimeout(() => controller.abort(), 300_000);
      let response: Response;
      try {
        response = await fetch(`https://aggie-course-planner-ai-jrvo.onrender.com/recommend/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });
      } finally {
        clearTimeout(requestTimeout);
      }

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        const details = errorBody?.detail
          ? JSON.stringify(errorBody.detail)
          : response.statusText || 'The recommendation service could not complete the request.';
        throw new Error(`Request failed (${response.status}): ${details}`);
      }

      const data: { recommendations: Recommendation[] } = await response.json();
      setRecommendations(data.recommendations ?? []);
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        setError('The recommendation request took too long. Please check that the backend is running, then try again.');
      } else {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
      }
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

      <div className="mx-auto grid max-w-7xl grid-cols-1 items-start gap-5 px-4 py-5 lg:grid-cols-12">
        
        {/* Left Column: Configuration Panel */}
        <div className="lg:col-span-4">
          <div className="rounded-3xl border border-gray-200 bg-white p-3 shadow-md shadow-[#022851]/5">
            <h2 className="mb-1 text-lg font-bold text-[#022851]">Plan for Winter Quarter 2027</h2>
            <p className="mb-3 text-xs text-gray-500">Tell AggieAI what you’re looking for.</p>

            <form id="recommendation-form" onSubmit={handleSearch} className="flex flex-col gap-2">
              <div>
                <div className="rounded-2xl border-2 border-[#B3A369] bg-gradient-to-br from-amber-50 to-white p-2.5 shadow-sm">
                  <label htmlFor="academic-interests" className="mb-1 block text-sm font-bold text-gray-900">
                    Academic Interests <span className="text-red-600" aria-label="required">*</span>
                  </label>
                  <p className="mb-1.5 text-xs text-gray-600">
                    Describe the class you want to take for next quarter.
                  </p>
                  <textarea 
                    id="academic-interests"
                    required
                    rows={4}
                    className="min-h-24 w-full rounded-xl border border-gray-300 bg-white p-2.5 text-sm leading-5 focus:border-[#B3A369] focus:ring-2 focus:ring-[#B3A369]/50 outline-none transition-all resize-y"
                    placeholder="E.g. I am interested in psychology and movies"
                    value={interests}
                    onChange={(e) => setInterests(e.target.value)}
                  />
                </div>
              </div>

              <div className="rounded-xl border border-[#B3A369]/70 bg-amber-50/70 p-2">
                <label htmlFor="student-level" className="mb-1 block text-xs font-bold text-gray-900">
                  Student Level <span className="text-red-600" aria-label="required">*</span>
                </label>
                <select
                  id="student-level"
                  required
                  aria-required="true"
                  className="w-full rounded-lg border border-gray-200 bg-white p-2 text-xs focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                  value={studentLevel}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '' || value === 'undergraduate' || value === 'lower' || value === 'upper' || value === 'graduate') {
                      setStudentLevel(value);
                    }
                  }}
                >
                  <option value="" disabled>Please select a student level</option>
                  <option value="undergraduate">All undergraduate courses</option>
                  <option value="lower">Lower division undergraduate (001–099)</option>
                  <option value="upper">Upper division undergraduate (100–199)</option>
                  <option value="graduate">Graduate (200+)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 content-start gap-2">
                <h3 className="col-span-2 rounded-xl bg-gradient-to-r from-[#022851] via-[#064477] to-[#B3A369] px-3 py-1.5 text-sm font-bold tracking-wide text-white shadow-md">
                  Advanced filters
                </h3>

                <div>
                  <label className="mb-1 block text-xs font-bold text-gray-700">Target GE</label>
                  <select 
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 p-2 text-xs focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                    value={ge}
                    onChange={(e) => setGe(e.target.value)}
                  >
                    <option value="Any">Any GE</option>
                    <option value="Arts & Humanities">Arts & Humanities (AH)</option>
                    <option value="Science & Engineering">Science & Engineering (SE)</option>
                    <option value="Social Sciences">Social Sciences (SS)</option>
                    <option value="American Cultures, Governance, & History">American Cultures, Governance, & History (ACGH)</option>
                    <option value="Domestic Diversity">Domestic Diversity (DD)</option>
                    <option value="Oral Skills">Oral Skills (OL)</option>
                    <option value="Quantitative Literacy">Quantitative Literacy (QL)</option>
                    <option value="Scientific Literacy">Scientific Literacy (SL)</option>
                    <option value="Visual Literacy">Visual Literacy (VL)</option>
                    <option value="World Cultures">World Cultures (WC)</option>
                    <option value="Writing Experience">Writing Experience (WE)</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-bold text-gray-700">Units</label>
                  <select 
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 p-2 text-xs focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none cursor-pointer"
                    value={units}
                    onChange={(e) => setUnits(e.target.value)}
                  >
                    <option value="Any">Any</option>
                    <option value="1">1 Unit</option>
                    <option value="2">2 Units</option>
                    <option value="3">3 Units</option>
                    <option value="4">4 Units</option>
                    <option value="5">5 Units</option>
                    <option value="6">6 Units</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="course-prefix" className="mb-1 block text-xs font-bold text-gray-700">Course Prefix</label>
                  <input
                    id="course-prefix"
                    maxLength={3}
                    autoCapitalize="characters"
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 p-2 text-xs uppercase focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none"
                    placeholder="e.g., ECS"
                    value={coursePrefix}
                    onChange={(e) => setCoursePrefix(e.target.value.replace(/[^a-z]/gi, '').slice(0, 3).toUpperCase())}
                  />
                </div>

                <div className="min-w-0">
                  <label className="mb-1 block text-xs font-bold text-gray-700">Completed Prerequisites</label>
                  <input 
                    type="text"
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 p-2 text-xs focus:bg-white focus:ring-2 focus:ring-[#B3A369]/50 outline-none"
                    placeholder="e.g., ECS 032A, MAT 021A"
                    value={completed}
                    onChange={(e) => setCompleted(e.target.value)}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="group mt-0.5 w-full cursor-pointer rounded-xl bg-gradient-to-r from-[#022851] to-[#07518c] px-4 py-4 text-sm font-bold text-white shadow-lg shadow-[#022851]/20 transition-all duration-200 hover:-translate-y-1 hover:from-[#064477] hover:to-[#B3A369] hover:shadow-xl hover:shadow-[#022851]/30 active:translate-y-0 active:scale-[0.99] disabled:cursor-wait disabled:opacity-70 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#B3A369]"
              >
                {isLoading ? 'Finding Winter 2027 Matches...' : 'Generate Recommendations'}
                {!isLoading && <span aria-hidden="true" className="ml-1 inline-block transition-transform duration-200 group-hover:translate-x-1"> →</span>}
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: AI Output */}
        <div className="lg:col-span-8 relative">
          
          {/* State 1: Empty / Landing (Only shows before first search) */}
          {!hasSearched && (
            <div className="flex min-h-[550px] flex-col items-center justify-center rounded-3xl border border-[#dbe3eb] bg-gradient-to-br from-white via-[#f7f9fc] to-[#e9f0f6] px-8 text-center shadow-sm">
              <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-[#022851] shadow-xl shadow-[#022851]/20 ring-4 ring-[#B3A369]/25">
                <svg aria-hidden="true" viewBox="0 0 48 48" className="h-12 w-12 fill-none">
                  <path d="M24 13c-5-4-11-4-17-2v23c6-2 12-2 17 2V13Z" fill="#B3A369" stroke="#E8DDAF" strokeWidth="2" strokeLinejoin="round" />
                  <path d="M24 13c5-4 11-4 17-2v23c-6-2-12-2-17 2V13Z" fill="#fff" stroke="#B3A369" strokeWidth="2" strokeLinejoin="round" />
                  <path d="M11 17c3-.7 6-.4 9 1M11 22c3-.7 6-.4 9 1M28 18c3-1.4 6-1.7 9-1M28 23c3-1.4 6-1.7 9-1" stroke="#022851" strokeWidth="1.8" strokeLinecap="round" />
                  <path d="M24 13v23" stroke="#022851" strokeWidth="2" />
                </svg>
              </div>
              <h3 className="mb-2 text-2xl font-bold text-[#022851]">Ready to explore?</h3>
              <p className="max-w-sm text-sm text-gray-500">
                Add your interests to get ranked course recommendations for Winter Quarter 2027.
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
                 <h4 className="font-bold mb-1">Could not get recommendations</h4>
                 <p className="text-sm">{error}</p>
               </div>
            </div>
          )}

          {/* State 4: Results Rendering */}
          {!isLoading && !error && hasSearched && recommendations.length > 0 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Top Winter 2027 Matches</h3>
                <span className="text-sm font-semibold text-[#B3A369]">Powered by all-MiniLM-L6-v2</span>
              </div>
              
              {recommendations.map((rec, index) => (
                <CourseCard
                  key={rec.course?.course_code ?? index}
                  rank={index + 1}
                  title={rec.course ? `${rec.course.course_code}: ${rec.course.title}` : "Course Title"}
                  description={rec.course?.description ?? ''}
                  details={rec.course?.details ?? ''}
                  units={rec.course?.units ?? 'Units not listed'}
                  prerequisites={rec.course?.prerequisites ?? ''}
                />
              ))}
            </div>
          )}

          {/* State 5: No Results Found */}
          {!isLoading && !error && hasSearched && recommendations.length === 0 && (
            <div className="text-center py-20 bg-white rounded-3xl border border-gray-100">
              <span className="text-4xl mb-4 block">🔍</span>
              <h3 className="text-lg font-bold text-gray-900">No ranked matches found for Winter 2027.</h3>
              <p className="text-gray-500 mt-2">
                Try broadening your interests or adjusting your GE, unit, course level, or subject filters.
              </p>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}