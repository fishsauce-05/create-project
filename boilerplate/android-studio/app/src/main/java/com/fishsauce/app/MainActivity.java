package com.fishsauce.app;

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home);

        TextView txtHello = findViewById(R.id.txtHello);
        txtHello.setText("Help me to develop: https://github.com/fishsauce-05/create-project");
    }
}