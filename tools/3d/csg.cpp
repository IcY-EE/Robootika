// Lihtne CSG-käsufailide täitja manifold teegiga.
// Rida: <op> <tüüp> <arvud...>   op: + (lisa) või - (lahuta)
//  B x0 y0 z0 x1 y1 z1            risttahukas
//  C x y z0 z1 r [seg]            püstsilinder (Z-telg)
//  K x y z0 z1 r0 r1 [seg]        koonus (Z-telg)
//  X y z x0 x1 r [seg]            silinder X-teljel
//  Y x z y0 y1 r [seg]            silinder Y-teljel
//  P z0 z1 n x1 y1 ... xn yn      hulknurga ekstrusioon
// Väljund: binaarne STL, nihutatud nii, et min x,y,z = 0.
#include <manifold/manifold.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <cstdint>
using namespace manifold;
int main(int argc,char**argv){
  if(argc<3){std::cerr<<"csg in.csg out.stl\n";return 1;}
  std::ifstream in(argv[1]);std::string line;std::vector<Manifold> add,sub,inter;
  while(std::getline(in,line)){
    if(line.empty()||line[0]=='#')continue;std::istringstream ss(line);std::string op,t;ss>>op>>t;Manifold m;
    if(t=="B"){double a[6];for(auto&v:a)ss>>v;m=Manifold::Cube({a[3]-a[0],a[4]-a[1],a[5]-a[2]}).Translate({a[0],a[1],a[2]});}
    else if(t=="C"||t=="K"){double x,y,z0,z1,r0,r1;int seg=48;ss>>x>>y>>z0>>z1>>r0;if(t=="K")ss>>r1;else r1=r0;if(!(ss>>seg))seg=48;
      m=Manifold::Cylinder(z1-z0,r0,r1,seg).Translate({x,y,z0});}
    else if(t=="X"){double y,z,x0,x1,r;int seg=32;ss>>y>>z>>x0>>x1>>r;if(!(ss>>seg))seg=32;m=Manifold::Cylinder(x1-x0,r,r,seg).Rotate(0,90,0).Translate({x0,y,z});}
    else if(t=="Y"){double x,z,y0,y1,r;int seg=32;ss>>x>>z>>y0>>y1>>r;if(!(ss>>seg))seg=32;m=Manifold::Cylinder(y1-y0,r,r,seg).Rotate(-90,0,0).Translate({x,y0,z});}
    else if(t=="P"){double z0,z1;int n;ss>>z0>>z1>>n;SimplePolygon p;for(int i=0;i<n;i++){double x,y;ss>>x>>y;p.push_back({x,y});}
      m=Manifold::Extrude(Polygons{p},z1-z0).Translate({0,0,z0});}
    else {std::cerr<<"tundmatu: "<<line<<"\n";return 2;}
    if(op=="*")inter.push_back(m); else (op=="+"?add:sub).push_back(m);
  }
  Manifold r=Manifold::BatchBoolean(add,OpType::Add);
  if(!sub.empty()) r=r-Manifold::BatchBoolean(sub,OpType::Add);
  for(auto&m:inter) r=r^m;
  auto bb=r.BoundingBox();if(!(argc>3&&std::string(argv[3])=="raw"))r=r.Translate({-bb.min.x,-bb.min.y,-bb.min.z});
  MeshGL mg=r.GetMeshGL();size_t nt=mg.triVerts.size()/3;int np=mg.numProp;
  std::ofstream o(argv[2],std::ios::binary);char hdr[80]={0};snprintf(hdr,80,"AI-kabelaud %s",argv[2]);o.write(hdr,80);uint32_t n32=nt;o.write((char*)&n32,4);
  for(size_t i=0;i<nt;i++){float v[12]={0};float P[3][3];for(int k=0;k<3;k++){int vi=mg.triVerts[3*i+k];for(int j=0;j<3;j++)P[k][j]=mg.vertProperties[vi*np+j];}
    float ux=P[1][0]-P[0][0],uy=P[1][1]-P[0][1],uz=P[1][2]-P[0][2],wx=P[2][0]-P[0][0],wy=P[2][1]-P[0][1],wz=P[2][2]-P[0][2];
    v[0]=uy*wz-uz*wy;v[1]=uz*wx-ux*wz;v[2]=ux*wy-uy*wx;float l=sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);if(l>0){v[0]/=l;v[1]/=l;v[2]/=l;}
    for(int k=0;k<3;k++)for(int j=0;j<3;j++)v[3+3*k+j]=P[k][j];o.write((char*)v,48);uint16_t a=0;o.write((char*)&a,2);}
  auto b2=r.BoundingBox();
  std::cout<<argv[2]<<": "<<nt<<" kolmnurka, "<<(b2.max.x-b2.min.x)<<" x "<<(b2.max.y-b2.min.y)<<" x "<<(b2.max.z-b2.min.z)<<" mm, maht "<<r.Volume()/1000<<" cm3, genus "<<r.Genus()<<(r.Status()==Manifold::Error::NoError?"":" VIGA")<<"\n";
}
