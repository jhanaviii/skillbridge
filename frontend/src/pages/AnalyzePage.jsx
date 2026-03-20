import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchProfiles, fetchJobs, analyzeGap, createProfile, updateProfile } from '../api';
import SkillPill from '../components/SkillPill';
import LoadingSpinner from '../components/LoadingSpinner';

const roleFilters = ['All', 'Cloud Engineer', 'Frontend Developer', 'Security Analyst'];
const roleOptions = ['Cloud Engineer', 'Frontend Developer', 'Security Analyst'];

export default function AnalyzePage() {
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [roleFilter, setRoleFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Profile creation state
  const [profileTab, setProfileTab] = useState('existing'); // 'existing' | 'create'
  const [newProfile, setNewProfile] = useState({
    name: '', email: '', current_skills: [], years_experience: 1,
    education: '', target_role: 'Cloud Engineer', background_summary: '',
  });
  const [newSkillInput, setNewSkillInput] = useState('');
  const [creating, setCreating] = useState(false);

  // Edit skills state
  const [editing, setEditing] = useState(false);
  const [editSkills, setEditSkills] = useState([]);
  const [editSkillInput, setEditSkillInput] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [p, j] = await Promise.all([fetchProfiles(), fetchJobs()]);
        setProfiles(p);
        setJobs(j);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredJobs = roleFilter === 'All'
    ? jobs
    : jobs.filter((j) => j.role_category === roleFilter);

  async function handleAnalyze() {
    if (!selectedProfile || !selectedJob) return;
    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeGap(selectedProfile.id, selectedJob.id);
      navigate('/results', { state: { result, profile: selectedProfile, job: selectedJob } });
    } catch (e) {
      setError(e.message);
      setAnalyzing(false);
    }
  }

  // --- Create Profile ---
  function addNewSkill(e) {
    if (e.key === 'Enter' && newSkillInput.trim()) {
      e.preventDefault();
      const s = newSkillInput.trim().toLowerCase();
      if (!newProfile.current_skills.includes(s)) {
        setNewProfile({ ...newProfile, current_skills: [...newProfile.current_skills, s] });
      }
      setNewSkillInput('');
    }
  }
  function removeNewSkill(skill) {
    setNewProfile({ ...newProfile, current_skills: newProfile.current_skills.filter((s) => s !== skill) });
  }
  async function handleCreate() {
    if (!newProfile.name || !newProfile.email || newProfile.current_skills.length === 0) {
      setError('Name, email, and at least one skill are required');
      return;
    }
    setCreating(true);
    setError(null);
    try {
      const created = await createProfile(newProfile);
      const refreshed = await fetchProfiles();
      setProfiles(refreshed);
      setSelectedProfile(created);
      setProfileTab('existing');
      setNewProfile({ name: '', email: '', current_skills: [], years_experience: 1, education: '', target_role: 'Cloud Engineer', background_summary: '' });
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  }

  // --- Edit Skills ---
  function openEditSkills() {
    setEditSkills([...selectedProfile.current_skills]);
    setEditing(true);
  }
  function addEditSkill(e) {
    if (e.key === 'Enter' && editSkillInput.trim()) {
      e.preventDefault();
      const s = editSkillInput.trim().toLowerCase();
      if (!editSkills.includes(s)) setEditSkills([...editSkills, s]);
      setEditSkillInput('');
    }
  }
  function removeEditSkill(skill) {
    setEditSkills(editSkills.filter((s) => s !== skill));
  }
  async function saveEditSkills() {
    if (editSkills.length === 0) { setError('At least one skill required'); return; }
    setSaving(true);
    setError(null);
    try {
      const updated = await updateProfile(selectedProfile.id, { current_skills: editSkills });
      const refreshed = await fetchProfiles();
      setProfiles(refreshed);
      setSelectedProfile(updated);
      setEditing(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingSpinner message="Loading profiles and jobs..." />;
  if (analyzing) return <LoadingSpinner message="Running AI-powered skill gap analysis..." />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-2">Analyze Skill Gap</h1>
      <p className="text-slate-400 mb-8">Select a candidate profile and a target job to compare</p>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-300 text-sm mb-6">
          {error}
          <button onClick={() => setError(null)} className="ml-3 text-red-400 hover:text-red-300">✕</button>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8 mb-10">
        {/* ==================== LEFT: Profile ==================== */}
        <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">👤 Candidate Profile</h2>

          {/* Tabs */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setProfileTab('existing')}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all ${profileTab === 'existing' ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' : 'border-slate-600 text-slate-400 hover:border-slate-500'}`}
            >Choose Existing</button>
            <button
              onClick={() => setProfileTab('create')}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all ${profileTab === 'create' ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' : 'border-slate-600 text-slate-400 hover:border-slate-500'}`}
            >Create New</button>
          </div>

          {profileTab === 'existing' ? (
            <>
              <select
                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none"
                value={selectedProfile?.id || ''}
                onChange={(e) => {
                  const p = profiles.find((x) => x.id === e.target.value);
                  setSelectedProfile(p || null);
                  setEditing(false);
                }}
              >
                <option value="">Select a profile...</option>
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} — {p.target_role}</option>
                ))}
              </select>

              {selectedProfile && (
                <div className="mt-4 space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div><span className="text-slate-500">Experience:</span> <span className="text-white">{selectedProfile.years_experience} years</span></div>
                    <div><span className="text-slate-500">Target:</span> <span className="text-white">{selectedProfile.target_role}</span></div>
                  </div>
                  <div className="text-sm"><span className="text-slate-500">Education:</span> <span className="text-white">{selectedProfile.education}</span></div>
                  <p className="text-xs text-slate-400 italic leading-relaxed">{selectedProfile.background_summary}</p>

                  <div className="pt-2">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-500">Current Skills</span>
                      <button onClick={openEditSkills} className="text-xs text-blue-400 hover:text-blue-300">Edit Skills ✎</button>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedProfile.current_skills.map((s) => <SkillPill key={s} skill={s} color="green" />)}
                    </div>
                  </div>

                  {/* Edit Skills Panel */}
                  {editing && (
                    <div className="mt-3 p-4 bg-slate-700/30 border border-slate-600 rounded-lg">
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {editSkills.map((s) => (
                          <span key={s} className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            {s}
                            <button onClick={() => removeEditSkill(s)} className="text-emerald-400 hover:text-red-400 ml-0.5">✕</button>
                          </span>
                        ))}
                      </div>
                      <input
                        className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                        placeholder="Type a skill and press Enter..."
                        value={editSkillInput}
                        onChange={(e) => setEditSkillInput(e.target.value)}
                        onKeyDown={addEditSkill}
                      />
                      <div className="flex gap-2 mt-3">
                        <button onClick={saveEditSkills} disabled={saving}
                          className="px-4 py-1.5 text-xs rounded bg-blue-500 hover:bg-blue-400 text-white font-medium">
                          {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                        <button onClick={() => setEditing(false)}
                          className="px-4 py-1.5 text-xs rounded bg-slate-600 hover:bg-slate-500 text-white">
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            /* ---- Create New Profile Form ---- */
            <div className="space-y-3">
              <input className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" placeholder="Full name" value={newProfile.name} onChange={(e) => setNewProfile({ ...newProfile, name: e.target.value })} />
              <input className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" placeholder="Email" type="email" value={newProfile.email} onChange={(e) => setNewProfile({ ...newProfile, email: e.target.value })} />
              <input className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" placeholder="Education (e.g. B.S. Computer Science, MIT)" value={newProfile.education} onChange={(e) => setNewProfile({ ...newProfile, education: e.target.value })} />

              <div>
                <label className="text-xs text-slate-500 block mb-1">Target Role</label>
                <select className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none" value={newProfile.target_role} onChange={(e) => setNewProfile({ ...newProfile, target_role: e.target.value })}>
                  {roleOptions.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-500 block mb-1">Years of Experience: {newProfile.years_experience}</label>
                <input type="range" min="0" max="5" step="0.5" value={newProfile.years_experience} onChange={(e) => setNewProfile({ ...newProfile, years_experience: parseFloat(e.target.value) })} className="w-full accent-blue-500" />
              </div>

              <textarea className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none resize-none" rows={2} placeholder="Brief background summary (2 sentences)" value={newProfile.background_summary} onChange={(e) => setNewProfile({ ...newProfile, background_summary: e.target.value })} />

              <div>
                <label className="text-xs text-slate-500 block mb-1">Skills (type + Enter)</label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {newProfile.current_skills.map((s) => (
                    <span key={s} className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {s}
                      <button onClick={() => removeNewSkill(s)} className="text-emerald-400 hover:text-red-400 ml-0.5">✕</button>
                    </span>
                  ))}
                </div>
                <input className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none" placeholder="e.g. python" value={newSkillInput} onChange={(e) => setNewSkillInput(e.target.value)} onKeyDown={addNewSkill} />
              </div>

              <button onClick={handleCreate} disabled={creating}
                className="w-full py-2.5 rounded-lg font-semibold text-sm bg-blue-500 hover:bg-blue-400 text-white transition-all disabled:bg-slate-600 disabled:cursor-not-allowed">
                {creating ? 'Creating...' : '+ Create Profile'}
              </button>
            </div>
          )}
        </div>

        {/* ==================== RIGHT: Job ==================== */}
        <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">💼 Target Job</h2>

          <div className="flex flex-wrap gap-2 mb-4">
            {roleFilters.map((r) => (
              <button key={r} onClick={() => setRoleFilter(r)}
                className={`text-xs px-3 py-1.5 rounded-full border transition-all ${roleFilter === r ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' : 'border-slate-600 text-slate-400 hover:border-slate-500'}`}>
                {r}
              </button>
            ))}
          </div>

          <select
            className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none"
            value={selectedJob?.id || ''}
            onChange={(e) => {
              const j = jobs.find((x) => x.id === e.target.value);
              setSelectedJob(j || null);
            }}
          >
            <option value="">Select a job...</option>
            {filteredJobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title} ({j.seniority}) — {j.company_type}</option>
            ))}
          </select>

          {selectedJob && (
            <div className="mt-4 space-y-3">
              <p className="text-xs text-slate-400 leading-relaxed">{selectedJob.description}</p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><span className="text-slate-500">Seniority:</span> <span className="text-white capitalize">{selectedJob.seniority}</span></div>
                <div><span className="text-slate-500">Company:</span> <span className="text-white capitalize">{selectedJob.company_type}</span></div>
                <div><span className="text-slate-500">Experience:</span> <span className="text-white">{selectedJob.min_years}–{selectedJob.max_years} years</span></div>
                <div><span className="text-slate-500">Category:</span> <span className="text-white">{selectedJob.role_category}</span></div>
              </div>
              <div className="pt-2">
                <span className="text-xs text-slate-500 block mb-2">Required Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedJob.required_skills.map((s) => <SkillPill key={s} skill={s} color="blue" />)}
                </div>
              </div>
              {selectedJob.nice_to_have.length > 0 && (
                <div className="pt-1">
                  <span className="text-xs text-slate-500 block mb-2">Nice to Have</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJob.nice_to_have.map((s) => <SkillPill key={s} skill={s} color="gray" />)}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Analyze button */}
      <div className="text-center">
        <button onClick={handleAnalyze} disabled={!selectedProfile || !selectedJob}
          className={`px-10 py-3.5 rounded-xl font-semibold text-lg transition-all ${selectedProfile && selectedJob ? 'bg-blue-500 hover:bg-blue-400 text-white shadow-lg shadow-blue-500/25 hover:-translate-y-0.5' : 'bg-slate-700 text-slate-500 cursor-not-allowed'}`}>
          🔍 Analyze Skill Gap
        </button>
        {(!selectedProfile || !selectedJob) && (
          <p className="text-xs text-slate-500 mt-3">Select both a profile and a job to continue</p>
        )}
      </div>
    </div>
  );
}
