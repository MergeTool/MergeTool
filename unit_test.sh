#setting up a new local git repository with two branches - master and new-branch
mkdir unit_test_dir
cd unit_test_dir
git init

touch unit_test_prog.cpp

touch Makefile
cat <<EOF > Makefile
prog: unit_test_prog.cpp
    g++ unit_test_prog.cpp
EOF

git add .
git commit -m "This is a commit no doubt"

git checkout -b new-branch
cat <<EOF > unit_test_prog.cpp
#include<iostream>
#include<cmath>
#include<cstdio>
#include<cstdlib>
 
using namespace std;
 
int main()
{
   int n, status = 1, num = 3, count, c;
 
   cout << "Enter the number of prime numbers to print\n";
   cin >> n;
   n += 1;
   printf("left");
 
   if ( n >= 1 )
   {
      cout << "First " << n <<" prime numbers are :-" << endl;
      cout << 2 << endl;
   }
 
   for ( count = 2 ; count <=n ;  )
   {
      for ( c = 2 ; c <= (int)sqrt(num) ; c++ )
      {
         if ( num%c == 0 )
         {
            status = 0;
            break;
         }
      }
      printf("hello, world!");
      status = 0;
      printf("left");
      c = 5;
      if ( status != 0 )
      {
         cout << num << endl;
         count++;
      }
      status = 1;
      num++;
   }         
 
   return 0;
}
EOF
git add .
git commit -m "This is smth completely different"

git checkout master
cat <<EOF > unit_test_prog.cpp
#include<iostream>
#include<cmath>
#include<cstdio>
#include<cstdlib>
 
using namespace std;
 
int main()
{
   int n, status = 1, num = 3, count, c;
 
   cout << "Enter the number of prime numbers to print\n";
   scanf("%d", &n);
   n -= 1;
   printf("right");
 
   if ( n >= 1 )
   {
      cout << "First " << n <<" prime numbers are :-" << endl;
      cout << 2 << endl;
   }
 
   for ( count = 2 ; count <=n ;  )
   {
      for ( c = 2 ; c <= (int)sqrt(num) ; c++ )
      {
         if ( num/c == 0 )
         {
            status = -1;
            continue;
         }
      }
      printf("hello, world!");
      status = 0;
      printf("right");
      c = 7;
      if ( status != 0 )
      {
         cout << num << endl;
         count++;
      }
      status = 1;
      num++;
   }         
 
   return 0;
}
EOF
git add .
git commit -m "This is smth else entirely"


#merging with conflicts
git merge new-branch
#resolving conflicts with mergetool
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "lalalalala $DIR \n"
python3 /usr/local/bin/mergetool/merger.py $DIR



#competing the merge

#This part is written assuming that future MergeTool beta 
#will be rewriting files it resolves conflicts in.
#If this will prove a bad idea delete all of the following
#otherwise, uncomment it:

#git add .
#git commit -m "Resolving a test merge conflict"
