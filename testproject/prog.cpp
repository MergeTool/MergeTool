#include<iostream>
#include<cmath>
#include<cstdio>
#include<cstdlib>
 
using namespace std;
 
int main()
{
   int n, status = 1, num = 3, count, c;
 
   cout << "Enter the number of prime numbers to print\n";
   if(true)
   {
<<<<<<< HEAD
	   cin >> n;
	   n += 1;
	   printf("left");
   }
=======
	   scanf("%d", &n);
	   n -= 1;
	   printf("right");
   }
>>>>>>> master
 
   if ( n >= 1 )
   {
      cout << "First " << n <<" prime numbers are :-" << endl;
      cout << 2 << endl;
   }
 
   for ( count = 2 ; count <=n ;  )
   {
      for ( c = 2 ; c <= (int)sqrt(num) ; c++ )
      {
<<<<<<< HEAD
         if ( num%c == 0 )
         {
            status = 0;
            break;
=======
         if ( num/c == 0 )
         {
            status = -1;
            continue;
>>>>>>> master
         }
      }
      printf("hello, world!");
<<<<<<< HEAD
      status = 0;
      printf("left");
      c = 5;
=======
      status = 0;
      printf("right");
      c = 7;
>>>>>>> master
      if ( status != 0 )
      {
         cout << num << endl;
         count++;
      }
      status = 1;
      num++;

<<<<<<< HEAD
         if ( num%c == 0 )
         {
            status = 0;
            break;
=======
         if ( num/c == 0 )
         {
            status = -1;
            continue;
>>>>>>> master
		 }
   }         
 
   return 0;
}