using System;
using System.Collections.Generic;
using Il2CppHurricaneVR.Framework.Core.Grabbers;
using Il2CppHurricaneVR.Framework.Core.ScriptableObjects;
using Il2CppInterop.Runtime;
using MelonLoader;
using UnityEngine;

[assembly: MelonInfo(typeof(ForceBoost.Core), "ForceBoost", "1.0.0", "geom2543")]
[assembly: MelonGame("Kubunautilus", "BrutalistickVR")]

namespace ForceBoost
{
    // Force grab (pulling items to the hand) is HurricaneVR's HVRForceGrabber. How hard and fast it pulls
    // lives in shared HVRForcePullSettings assets (pull, push and per-item overrides), so we find all of
    // them and multiply their force and speed. Gravity-glove style grabbers get a shorter flight time.
    public class Core : MelonMod
    {
        private MelonPreferences_Category _cat;
        private MelonPreferences_Entry<bool> _enabled;
        private MelonPreferences_Entry<float> _force;
        private MelonPreferences_Entry<float> _speed;
        private MelonPreferences_Entry<bool> _verbose;

        // What we last wrote, per asset. If the game (or a reload) puts a different value back, it is
        // treated as a fresh original, so values never get multiplied twice.
        private readonly Dictionary<IntPtr, (float accel, float speed, float slerp)> _written = new();
        private readonly Dictionary<IntPtr, float> _writtenTime = new();
        private float _timer;

        public override void OnInitializeMelon()
        {
            _cat = MelonPreferences.CreateCategory("ForceBoost");
            _enabled = _cat.CreateEntry("Enabled", true, "Enabled");
            _force = _cat.CreateEntry("ForceMultiplier", 10f, "Force x",
                "Multiplies the force-pull acceleration force (and the force that turns the item into your hand)");
            _speed = _cat.CreateEntry("SpeedMultiplier", 3f, "Speed x",
                "Multiplies the top speed items fly to your hand at (gravity-glove style: flight time is divided by it)");
            _verbose = _cat.CreateEntry("Verbose", true, "Verbose log");
            LoggerInstance.Msg($"Loaded. Force pull x{_force.Value}, speed x{_speed.Value}.");
        }

        public override void OnSceneWasInitialized(int buildIndex, string sceneName) => _timer = 0.5f;

        public override void OnUpdate()
        {
            if (!_enabled.Value) return;
            _timer -= Time.unscaledDeltaTime;
            if (_timer > 0f) return;
            _timer = 2f; // new items with their own settings can spawn at any time
            try { Apply(); }
            catch (Exception e) { LoggerInstance.Warning("Apply: " + e.Message); _timer = 10f; }
        }

        private void Apply()
        {
            float f = Mathf.Max(0f, _force.Value), s = Mathf.Max(0.01f, _speed.Value);

            foreach (var o in Resources.FindObjectsOfTypeAll(Il2CppType.Of<HVRForcePullSettings>()))
            {
                var p = o?.TryCast<HVRForcePullSettings>();
                if (p == null) continue;
                if (_written.TryGetValue(p.Pointer, out var w) &&
                    Mathf.Approximately(w.accel, p.MaxAccelerationForce) &&
                    Mathf.Approximately(w.speed, p.MaxSpeed) &&
                    Mathf.Approximately(w.slerp, p.SlerpMaxForce)) continue;

                float a0 = p.MaxAccelerationForce, v0 = p.MaxSpeed, sl0 = p.SlerpMaxForce;
                p.MaxAccelerationForce = a0 * f;
                p.MaxSpeed = v0 * s;
                if (!float.IsInfinity(sl0) && sl0 < 1e30f) p.SlerpMaxForce = sl0 * f;
                _written[p.Pointer] = (p.MaxAccelerationForce, p.MaxSpeed, p.SlerpMaxForce);
                if (_verbose.Value)
                    LoggerInstance.Msg($"'{p.name}': accel {a0:F0} -> {p.MaxAccelerationForce:F0}, speed {v0:F1} -> {p.MaxSpeed:F1}, turn force {sl0:F0} -> {p.SlerpMaxForce:F0}");
            }

            foreach (var o in Resources.FindObjectsOfTypeAll(Il2CppType.Of<HVRForceGrabber>()))
            {
                var g = o?.TryCast<HVRForceGrabber>();
                if (g == null) continue;
                if (_writtenTime.TryGetValue(g.Pointer, out var t) && Mathf.Approximately(t, g.ForceTime)) continue;
                float t0 = g.ForceTime;
                if (t0 > 0f) g.ForceTime = t0 / s;
                _writtenTime[g.Pointer] = g.ForceTime;
                if (_verbose.Value)
                    LoggerInstance.Msg($"Grabber '{g.name}' style {g.GrabStyle}: glove flight time {t0:F2} -> {g.ForceTime:F2}");
            }
        }
    }
}
