    // Toggle sidebar collapsed state for small screens
    (function(){
      const sb = document.getElementById('sidebar');
      const toggle = document.getElementById('sidebar-toggle');
      if (toggle) toggle.addEventListener('click', function(){
        sb.classList.toggle('collapsed');
      });

      // Optional: close sidebar when clicking outside on small screens
      document.addEventListener('click', function(e){
        if(window.innerWidth<=900){
          if(!sb.contains(e.target) && !toggle.contains(e.target)){
            sb.classList.add('collapsed');
          }
        }
      });
    })();