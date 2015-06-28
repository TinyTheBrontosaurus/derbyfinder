#include <dlib/svm_threaded.h>
#include <dlib/gui_widgets.h>
#include <dlib/image_processing.h>
#include <dlib/data_io.h>
#include <dlib/cmd_line_parser.h>

#include <iostream>
#include <fstream>


using namespace std;
using namespace dlib;



// ----------------------------------------------------------------------------------------

int main(int argc, char** argv)
{
  typedef scan_fhog_pyramid<pyramid_down<6> > image_scanner_type;
  object_detector<image_scanner_type> detector;
  const std::string images_directory = "../";
  try
    {
      command_line_parser parser;
      parser.add_option( "h", "Display this help message.");
      parser.add_option( "s", "Display the sticks visualization.");
      parser.add_option( "t", "Train detector and save to disk.");
      parser.add_option( "v", "Validate (test) detector against test data.");
      parser.add_option( "i", "Show images." );
      parser.add_option( "d", "Specify the detector to use.", 1);
      parser.add_option( "f", "Specify the input images XML file.", 1 );
      parser.add_option( "noflip", "Don't flip while training." );
      
      parser.parse( argc, argv );

      const char* one_time_opts[] = {"h", "s", "t", "v", "d", "f" };
      parser.check_one_time_options(one_time_opts);

      const char* incompatible[] = {"h", "s", "t", "v"};
      parser.check_incompatible_options(incompatible);

      const char* detector_ops[] = {"s", "t", "v"};
      const char* detector_sub_ops[] = {"d"};
      parser.check_sub_options(detector_ops, detector_sub_ops);

      const char* train_ops[] = {"t"};
      const char* train_sub_ops[] = {"noflip"};      
      parser.check_sub_options(train_ops, train_sub_ops );
      
      const char* images_ops[] = {"t", "v"};
      const char* images_sub_ops[] = {"f"};      
      parser.check_sub_options(images_ops, images_sub_ops );

      const char* display_ops[] = {"v"};
      const char* display_sub_ops[] = {"i"}; 
      parser.check_sub_options(display_ops, display_sub_ops );
	
      std::string detectorFile = "../detector.svm";
      std::string imagesFile = "../grass.xml";
      
      if( parser.option( "h" ) )
	{
	  printf( "Usage: %s [options]\n", argv[0] );
	  parser.print_options();
	  return EXIT_SUCCESS;
	}

      if( parser.option( "d" ) )
	{
	  detectorFile = parser.option( "d" ).argument();
	}

      if( parser.option( "f" ) )
	{
	  imagesFile = parser.option( "f" ).argument();
	}
      
      if( parser.option( "s" ) )
	{
	  deserialize(detectorFile) >> detector;
	  image_window hogwin(draw_fhog(detector), "Learned fHOG detector");
	  cout << "Press enter to exit" << endl;
	  cin.get();
	}
      else if(  parser.option( "t" ) )
	{	  	  
	  dlib::array<array2d<unsigned char> > images_train;
	  std::vector<std::vector<rectangle> > boxes_train;
	  
	  // Load the imagery
	  cout << "Loading" << endl;
	  load_image_dataset(images_train, boxes_train, imagesFile);
	  cout << "Upsampling" << endl;
	  upsample_image_dataset<pyramid_down<2> >(images_train, boxes_train);
	  if( false == parser.option( "noflip" ) )
	    {
	      cout << "Flipping out" << endl;
	      add_image_left_right_flips(images_train, boxes_train);
	    }

	  cout << "num training images: " << images_train.size() << endl;

	  // Setup the trainer
	  image_scanner_type scanner;
	  
	  scanner.set_detection_window_size(80, 80); 
	  structural_object_detection_trainer<image_scanner_type> trainer(scanner);
	  
	  trainer.set_num_threads(4);  
	  trainer.set_c(1);
	  trainer.be_verbose();
	  
	  // Run the trainer
	  object_detector<image_scanner_type> detector = trainer.train(images_train, boxes_train);

	  // Evaluate the results
	  cout << "training results: "
	       << test_object_detection_function(detector, images_train, boxes_train)
	       << endl;
	  cout << "num filters: "<< num_separable_filters(detector) << endl;

	  // Save the results
	  cout << "Saving to " << detectorFile << endl;
	  serialize( detectorFile ) << detector;
	}
      else if( parser.option( "v" ) )
	{
	  // Open the detector file	  
	  deserialize(detectorFile) >> detector;
	
	  dlib::array<array2d<unsigned char> > images_test;
	  std::vector<std::vector<rectangle> > boxes_test;
	  load_image_dataset(images_test, boxes_test, imagesFile);

	  cout << test_object_detection_function(detector, images_test, boxes_test);

	  if(  parser.option( "i" ) )
	    {
	      // Now for the really fun part.  Let's display the testing images on the screen and
	      // show the output of the face detector overlaid on each image.  You will see that
	      // it finds all the faces without false alarming on any non-faces.
	      image_window win; 
	      for (unsigned long i = 0; i < images_test.size(); ++i)
		{
		  // Run the detector and get the face detections.
		  std::vector<rectangle> dets = detector(images_test[i]);
		  win.clear_overlay();
		  win.set_image(images_test[i]);
		  win.add_overlay(dets, rgb_pixel(255,0,0));
		  cout << "Hit enter to process the next image..." << endl;
		  cin.get();
		}
	    }
	}
      else
	{
	  printf( "Usage: %s [options]\n", argv[0] );
	  parser.print_options();
	}             
    }
    catch (exception& e)
    {
        cout << "\nexception thrown!" << endl;
        cout << e.what() << endl;
    }
}

// ----------------------------------------------------------------------------------------

