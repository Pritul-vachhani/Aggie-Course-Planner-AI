'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const GE_CATEGORIES = [
  "Any",
  "Arts & Humanities (AH)",
  "Science & Engineering (SE)",
  "Social Sciences (SS)",
  "American Cultures, Governance, & History (ACGH)",
  "Domestic Diversity (DD)",
  "Oral Skills/Literacy (OL)",
  "Quantitative Literacy (QL)",
  "Scientific Literacy (SL)",
  "Visual Literacy (VL)",
  "World Cultures (WC)",
  "Writing Experience (WE)"
];

const MAJORS = [
  "Any",
  "Aerospace Science & Engineering",
  "African American & African Studies",
  "Agricultural & Environmental Chemistry",
  "Agricultural & Environmental Technology",
  "Agricultural & Resource Economics",
  "Agricultural Education",
  "American Studies",
  "Anatomy, Physiology, & Cell Biology",
  "Anesthesiology",
  "Animal Behavior",
  "Animal Biology",
  "Animal Genetics",
  "Animal Science",
  "Anthropology",
  "Economics",
  "Engineering Computer Science",
  "Engineering Electrical & Computer"
];

export default function PreferenceForm() {
  const router = useRouter();
  
  const [interests, setInterests] = useState('');
  const [ge, setGe] = useState('Any');
  const [units, setUnits] = useState('Any');
  const [major, setMajor] = useState('Any');
  const [completed, setCompleted] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    const params = new URLSearchParams({
      interests,
      ge,
      units,
      major,
      completed
    });

    router.push(`/results?${params.toString()}`);
  };

  return (
    <div className="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 relative overflow-hidden">
      {/* Decorative top border in Aggie Gold */}
      <div className="absolute top-0 left-0 w-full h-2 bg-[#B3A369]"></div>
      
      <div className="mb-6">
        <h2 className="text-2xl font-extrabold text-black tracking-tight">Design Your Quarter</h2>
        <p className="text-black text-sm mt-1">Tell AggieAI what you&apos;re looking for.</p>
      </div>
      
      <form onSubmit={handleSearch} className="space-y-5">
        <div>
          <label className="block text-sm font-semibold text-black mb-1">
            Academic Interests & Topics <span className="text-black">*</span>
          </label>
          <textarea 
            required
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="e.g., I need a chill class about film, psychology, or modern technology..." 
            className="w-full text-black placeholder:text-black border border-gray-200 rounded-lg p-3 min-h-[100px] focus:ring-2 focus:ring-[#B3A369] focus:border-transparent outline-none transition shadow-sm resize-none" 
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-black mb-1">GE</label>
            <select 
              value={ge}
              onChange={(e) => setGe(e.target.value)}
              className="w-full text-black border border-gray-200 rounded-lg p-3 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[#B3A369] outline-none transition cursor-pointer text-sm"
            >
              {GE_CATEGORIES.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-black mb-1">Units</label>
            <select 
              value={units}
              onChange={(e) => setUnits(e.target.value)}
              className="w-full text-black border border-gray-200 rounded-lg p-3 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[#B3A369] outline-none transition cursor-pointer text-sm"
            >
              <option value="Any">Any</option>
              <option value="1">1 Unit</option>
              <option value="2">2 Units</option>
              <option value="3">3 Units</option>
              <option value="4">4 Units</option>
              <option value="5">5 Units</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-black mb-1">Major</label>
          <select 
            value={major}
            onChange={(e) => setMajor(e.target.value)}
            className="w-full text-black border border-gray-200 rounded-lg p-3 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[#B3A369] outline-none transition cursor-pointer text-sm truncate"
          >
            {MAJORS.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-black mb-1">
            Completed Courses <span className="text-black font-normal">(Optional)</span>
          </label>
          <input 
            type="text"
            value={completed}
            onChange={(e) => setCompleted(e.target.value)}
            placeholder="e.g., ECS 032A, MAT 021A"
            className="w-full text-black placeholder:text-black border border-gray-200 rounded-lg p-3 focus:ring-2 focus:ring-[#B3A369] outline-none transition shadow-sm text-sm"
          />
        </div>

        <button 
          type="submit" 
          className="w-full bg-[#B3A369] text-black font-bold py-4 rounded-lg hover:bg-[#c4b47f] hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 mt-4"
        >
          Generate Recommendations
        </button>
      </form>
    </div>
  );
}