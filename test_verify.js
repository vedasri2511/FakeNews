const axios = require('axios');
(async ()=>{
  try{
    const r = await axios.post('http://localhost:5000/api/verify',{text:'Dhoni keeps wickets moves closer'}, {timeout:10000});
    console.log(r.status);
    console.log(JSON.stringify(r.data,null,2));
  }catch(e){
    if(e.response){console.error('Status', e.response.status); console.error(e.response.data);} else {console.error(e.message)}
  }
})();